import json
import os
from datetime import datetime, timezone
from pathlib import Path

from domain.seasonality import get_season_flag
from models.product import ProductDomain, ProductModel, ProductOption

_SAMPLE_PATH = Path(__file__).parent / "sample_data" / "naver_commerce_sample.json"


async def collect(context: dict) -> dict:
    use_real = bool(os.environ.get("NAVER_COMMERCE_CLIENT_ID"))
    if use_real:
        return await _collect_real(context)
    return _collect_mock(context)


# --- Real ---

async def _collect_real(context: dict) -> dict:
    from clients import naver_commerce as client

    season_flag  = context.get("season_flag", "비수기")
    collected_at = datetime.now(timezone.utc).isoformat()

    raw_products = client.get_channel_products(page=1, page_size=100)
    order_stats  = client.get_product_order_stats(days=30)  # 최근 30일 주문 집계

    # 그룹상품 대표명 사전 수집 (groupProductNo별 1회 API 호출)
    unique_groups = {str(p.get("groupProductNo", "") or "") for p in raw_products}
    unique_groups.discard("")
    group_name_map: dict[str, str] = {}
    for gpn in unique_groups:
        name = client.get_group_product_name(gpn)
        if name:
            group_name_map[gpn] = name

    products = [
        _real_to_product_model(p, season_flag, collected_at, order_stats, group_name_map)
        for p in raw_products
    ]

    return {
        "source":   "naver_commerce",
        "mode":     "real",
        "total":    len(products),
        "products": [p.model_dump() for p in products],
    }


def _real_to_product_model(
    raw: dict,
    season_flag: str,
    collected_at: str,
    order_stats: dict[str, dict] | None = None,
    group_name_map: dict[str, str] | None = None,
) -> ProductModel:
    name       = raw.get("name", "")
    sale_price = float(raw.get("discountedPrice") or raw.get("salePrice", 0))
    stock      = raw.get("stockQuantity", 0)

    # 주문 집계 — productId = channelProductNo 기준으로 매칭
    channel_id = str(raw.get("channelProductNo", ""))
    stats      = (order_stats or {}).get(channel_id, {})

    origin_no    = str(raw.get("originProductNo", "") or raw.get("channelProductNo", ""))
    product_type = _infer_product_type(name)
    weight_kg    = _infer_weight_kg(name, [])
    tags         = [t.get("text", "") for t in raw.get("sellerTags", [])]

    return ProductModel(
        product_id=origin_no,
        platform="naver",
        name=name,
        price=sale_price,
        options=[ProductOption(name="기본", price_delta=0.0, stock=stock)],
        sales_count=stats.get("quantity", 0),
        sales_revenue=stats.get("revenue", 0),
        review_count=0,   # 리뷰 API 별도
        review_score=0.0,
        category=raw.get("wholeCategoryName", ""),
        tags=tags,
        domain=ProductDomain(
            product_type=product_type,
            weight_kg=weight_kg,
            unit_price_per_kg=round(sale_price / weight_kg, 0) if weight_kg > 0 else 0.0,
            season_flag=season_flag,
        ),
        collected_at=collected_at,
        group_product_no=str(raw.get("groupProductNo", "") or ""),
        group_product_name=(group_name_map or {}).get(str(raw.get("groupProductNo", "") or ""), ""),
    )


def _infer_product_type(name: str) -> str:
    name_lower = name
    if "즙" in name_lower:
        return "즙"
    if "냉동" in name_lower or "급냉" in name_lower:
        return "냉동"
    if "생" in name_lower or "냉장" in name_lower:
        return "생과"
    return "가공품"


def _infer_weight_kg(name: str, options: list) -> float:
    import re
    targets = [name] + [o.name for o in options]
    for text in targets:
        m = re.search(r"(\d+(?:\.\d+)?)\s*kg", text, re.IGNORECASE)
        if m:
            unit_kg = float(m.group(1))
        else:
            m = re.search(r"(\d+)\s*g(?!\w)", text, re.IGNORECASE)
            if m:
                unit_kg = float(m.group(1)) / 1000
            else:
                continue
        # 세트 구성 개수 감지 — 예: "1kg, 3개" → 총 3kg
        m_count = re.search(r"[,×x\s]\s*(\d+)\s*개", text)
        if m_count:
            unit_kg *= int(m_count.group(1))
        return unit_kg
    return 1.0  # 기본값


# --- Mock ---

def _collect_mock(context: dict) -> dict:
    raw = _load_sample()
    season_flag = context.get("season_flag", "비수기")
    collected_at = datetime.now(timezone.utc).isoformat()

    products = [
        _sample_to_product_model(p, season_flag, collected_at)
        for p in raw["products"]
    ]

    return {
        "source":   "naver_commerce",
        "mode":     "mock",
        "total":    len(products),
        "products": [p.model_dump() for p in products],
    }


def _load_sample() -> dict:
    with open(_SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _sample_to_product_model(raw: dict, season_flag: str, collected_at: str) -> ProductModel:
    domain_raw = raw.get("domain", {})
    weight_kg: float = domain_raw.get("weight_kg", 0.0)
    price: float = float(raw["salePrice"])

    options = [
        ProductOption(
            name=opt["optionName"],
            price_delta=float(opt["price"]),
            stock=opt["stockQuantity"],
        )
        for opt in raw.get("options", [])
    ]

    return ProductModel(
        product_id=raw["productNo"],
        platform="naver",
        name=raw["productName"],
        price=price,
        options=options,
        sales_count=raw["saleStatistics"]["totalSalesCount"],
        review_count=raw["reviewStatistics"]["totalReviewCount"],
        review_score=float(raw["reviewStatistics"]["averageReviewScore"]),
        category=raw["category"]["name"],
        tags=raw.get("tags", []),
        domain=ProductDomain(
            product_type=domain_raw["product_type"],
            weight_kg=weight_kg,
            unit_price_per_kg=round(price / weight_kg, 0) if weight_kg > 0 else 0.0,
            season_flag=season_flag,
        ),
        collected_at=collected_at,
    )
