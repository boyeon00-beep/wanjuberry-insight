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

    # 현재 실제 판매가: 상품 상세 API items[].salePrice 기준 (주문 이력 역산 가격은 변경 전 가격일 수 있음)
    current_prices: dict[str, float] = {}
    for p in raw_products:
        sid = str(p.get("sellerProductId", ""))
        try:
            detail = client.get_product_detail(sid)
            prices = [int(item.get("salePrice", 0)) for item in detail.get("items", []) if item.get("salePrice")]
            if prices:
                current_prices[sid] = float(min(prices))
        except Exception:
            pass  # 실패 시 revenue 역산 가격 사용

    products = [
        _build_product_model(p, revenue_stats, current_prices, season_flag, collected_at)
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
    vendorItemId도 함께 수집 — Wing 보고서 매칭용.
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
                stats[pid] = {"quantity": 0, "revenue": 0, "unit_price": 0, "vendor_item_ids": set()}

            qty         = int(item.get("quantity", 0))
            sale_amount = int(item.get("saleAmount", 0))
            stats[pid]["quantity"] += sign * qty
            stats[pid]["revenue"]  += sign * sale_amount

            # vendorItemId 수집 (Wing 보고서 매칭 key)
            vid = str(item.get("vendorItemId", ""))
            if vid and vid != "0":
                stats[pid]["vendor_item_ids"].add(vid)

            # 단가는 SALE 기준 마지막 값으로 갱신
            if sale_type == "SALE" and qty > 0:
                sale_price = int(item.get("salePrice", 0))
                stats[pid]["unit_price"] = sale_price // qty

    # set → list 직렬화
    for v in stats.values():
        v["vendor_item_ids"] = list(v["vendor_item_ids"])

    return stats


def _build_product_model(
    raw: dict,
    revenue_stats: dict[str, dict],
    current_prices: dict[str, float],
    season_flag: str,
    collected_at: str,
) -> ProductModel:
    seller_pid = str(raw.get("sellerProductId", ""))
    product_id = str(raw.get("productId", ""))       # 매출 매핑용
    name       = raw.get("sellerProductName", "")

    stats = revenue_stats.get(product_id, {})
    # 상품 상세 API의 현재 판매가 우선 사용, 없으면 주문 이력 역산 가격
    price = current_prices.get(seller_pid) or float(stats.get("unit_price", 0))
    sales_count   = max(0, stats.get("quantity", 0))
    sales_revenue = max(0, stats.get("revenue", 0))
    vendor_item_ids = stats.get("vendor_item_ids", [])

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
        vendor_item_ids=vendor_item_ids,
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
    if "냉동" in name or "급냉" in name:
        return "냉동"
    if "생" in name or "냉장" in name:
        return "생과"
    return "가공품"


def _infer_weight_kg(name: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*kg", name, re.IGNORECASE)
    if m:
        unit_kg = float(m.group(1))
    else:
        m = re.search(r"(\d+)\s*g(?!\w)", name, re.IGNORECASE)
        if m:
            unit_kg = float(m.group(1)) / 1000
        else:
            return 1.0
    # 세트 구성 개수 감지 — 예: "1kg, 3개" → 총 3kg
    m_count = re.search(r"[,×x\s]\s*(\d+)\s*개", name)
    if m_count:
        unit_kg *= int(m_count.group(1))
    return unit_kg


# --- Empty fallback (키 미설정 시) ---

def _collect_empty(context: dict) -> dict:
    return {
        "source":   "coupang",
        "mode":     "skip",
        "total":    0,
        "products": [],
    }
