import os
import re
from datetime import datetime, timezone

from domain.seasonality import get_season_flag
from models.product import ProductDomain, ProductModel, ProductOption


async def collect(context: dict) -> dict:
    use_real = bool(os.environ.get("COUPANG_ACCESS_KEY"))
    if use_real:
        return await _collect_real(context)
    return _collect_empty(context)


# --- Real ---

async def _collect_real(context: dict) -> dict:
    from clients import coupang as client

    season_flag  = context.get("season_flag", "비수기")
    collected_at = datetime.now(timezone.utc).isoformat()

    raw_products   = client.get_products()
    revenue_orders = client.get_revenue_history(days=30)
    revenue_stats  = _aggregate_revenue(revenue_orders)  # productId → {quantity, revenue, unit_price}

    products = [
        _build_product_model(p, revenue_stats, season_flag, collected_at)
        for p in raw_products
    ]

    return {
        "source":   "coupang",
        "mode":     "real",
        "total":    len(products),
        "products": [p.model_dump() for p in products],
    }


def _aggregate_revenue(orders: list[dict]) -> dict[str, dict]:
    """주문 목록에서 productId 기준으로 매출 집계.

    REFUND는 차감 처리. productId=0인 항목(시스템 조정)은 제외.
    """
    stats: dict[str, dict] = {}

    for order in orders:
        sale_type = order.get("saleType", "SALE")
        sign      = 1 if sale_type == "SALE" else -1

        for item in order.get("items", []):
            pid = str(item.get("productId", ""))
            if not pid or pid == "0":
                continue

            if pid not in stats:
                stats[pid] = {"quantity": 0, "revenue": 0, "unit_price": 0}

            qty         = int(item.get("quantity", 0))
            sale_amount = int(item.get("saleAmount", 0))
            stats[pid]["quantity"] += sign * qty
            stats[pid]["revenue"]  += sign * sale_amount

            # 단가는 SALE 기준 마지막 값으로 갱신
            if sale_type == "SALE" and qty > 0:
                sale_price = int(item.get("salePrice", 0))
                stats[pid]["unit_price"] = sale_price // qty

    return stats


def _build_product_model(
    raw: dict,
    revenue_stats: dict[str, dict],
    season_flag: str,
    collected_at: str,
) -> ProductModel:
    seller_pid = str(raw.get("sellerProductId", ""))
    product_id = str(raw.get("productId", ""))       # 매출 매핑용
    name       = raw.get("sellerProductName", "")

    stats      = revenue_stats.get(product_id, {})
    price      = float(stats.get("unit_price", 0))
    sales_count  = max(0, stats.get("quantity", 0))
    sales_revenue = max(0, stats.get("revenue", 0))

    product_type = _infer_product_type(name)
    weight_kg    = _infer_weight_kg(name)

    return ProductModel(
        product_id=seller_pid,
        platform="coupang",
        name=name,
        price=price,
        options=[ProductOption(name="기본", price_delta=0.0, stock=0)],
        sales_count=sales_count,
        sales_revenue=sales_revenue,
        review_count=0,
        review_score=0.0,
        category="",
        tags=[],
        domain=ProductDomain(
            product_type=product_type,
            weight_kg=weight_kg,
            unit_price_per_kg=round(price / weight_kg, 0) if weight_kg > 0 else 0.0,
            season_flag=season_flag,
        ),
        collected_at=collected_at,
    )


def _infer_product_type(name: str) -> str:
    if "즙" in name:
        return "즙"
    if "냉동" in name:
        return "냉동"
    if "생" in name or "냉장" in name:
        return "생과"
    return "가공품"


def _infer_weight_kg(name: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*kg", name, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s*g(?!\w)", name, re.IGNORECASE)
    if m:
        return float(m.group(1)) / 1000
    return 1.0


# --- Empty fallback (키 미설정 시) ---

def _collect_empty(context: dict) -> dict:
    return {
        "source":   "coupang",
        "mode":     "skip",
        "total":    0,
        "products": [],
    }
