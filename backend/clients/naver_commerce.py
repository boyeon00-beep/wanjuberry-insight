import base64
import os
import time
from collections import defaultdict
from datetime import date, timedelta

import bcrypt
import httpx

_BASE = "https://api.commerce.naver.com"

_token_cache: dict = {"token": None, "expires_at": 0}


def _get_token() -> str:
    now = time.time()
    # 만료 30초 전에 갱신
    if _token_cache["token"] and now < _token_cache["expires_at"] - 30:
        return _token_cache["token"]

    client_id     = os.environ["NAVER_COMMERCE_CLIENT_ID"]
    client_secret = os.environ["NAVER_COMMERCE_CLIENT_SECRET"]
    timestamp     = str(int(now * 1000))

    password  = f"{client_id}_{timestamp}".encode("utf-8")
    salt      = client_secret.encode("utf-8")
    hashed    = bcrypt.hashpw(password, salt)
    signature = base64.b64encode(hashed).decode("utf-8")

    res = httpx.post(
        f"{_BASE}/external/v1/oauth2/token",
        data={
            "grant_type":         "client_credentials",
            "client_id":          client_id,
            "timestamp":          timestamp,
            "client_secret_sign": signature,
            "type":               "SELF",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    res.raise_for_status()
    body = res.json()
    _token_cache["token"]      = body["access_token"]
    _token_cache["expires_at"] = now + body.get("expires_in", 3600)
    return _token_cache["token"]


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}"}


_ACTIVE_DISPLAY_STATUSES = {"SALE", "OUTOFSTOCK"}


def get_channel_products(page: int = 1, page_size: int = 100) -> list[dict]:
    """상품 목록 조회 — 판매중/품절 상품만, originProductNo 포함 flat list 반환"""
    res = httpx.post(
        f"{_BASE}/external/v1/products/search",
        json={"page": page, "size": page_size},
        headers=_auth_headers(),
        timeout=15,
    )
    res.raise_for_status()
    contents = res.json().get("contents", [])

    products = []
    for item in contents:
        origin_no = str(item.get("originProductNo", ""))
        for cp in item.get("channelProducts", []):
            status = cp.get("channelProductDisplayStatusType", "")
            if status not in _ACTIVE_DISPLAY_STATUSES:
                continue
            products.append({**cp, "originProductNo": origin_no})
    return products


def get_product_order_stats(days: int = 30) -> dict[str, dict]:
    """주문 데이터를 집계해 상품별 sales_stats 반환.

    반환 형식: { productId: { order_count, quantity, revenue } }
    days: 오늘 기준 며칠치 주문을 집계할지 (기본 30일)
    API 제약: from/to 최대 24시간 차이 → 하루씩 루프
    """
    today = date.today()
    stats: dict[str, dict] = defaultdict(lambda: {"order_count": 0, "quantity": 0, "revenue": 0})

    for i in range(days):
        day     = today - timedelta(days=i)
        from_dt = day.strftime("%Y-%m-%dT00:00:00.000+09:00")
        to_dt   = day.strftime("%Y-%m-%dT23:59:59.999+09:00")
        _fetch_day_orders(from_dt, to_dt, stats)
        time.sleep(0.5)  # 레이트 리밋 방지

    return dict(stats)


def _fetch_day_orders(from_dt: str, to_dt: str, stats: dict) -> None:
    page, page_size = 1, 300
    while True:
        res = httpx.get(
            f"{_BASE}/external/v1/pay-order/seller/product-orders",
            params={
                "from":                 from_dt,
                "to":                   to_dt,
                "rangeType":            "PAYED_DATETIME",
                "productOrderStatuses": "PAYED,DELIVERING,DELIVERED,PURCHASE_DECIDED",
                "page":                 page,
                "size":                 page_size,
            },
            headers=_auth_headers(),
            timeout=20,
        )
        res.raise_for_status()
        body = res.json()

        contents = body.get("data", {}).get("contents", [])
        for item in contents:
            order = item.get("content", {}).get("productOrder", {})
            pid   = str(order.get("productId", ""))
            if not pid:
                continue
            stats[pid]["order_count"] += 1
            stats[pid]["quantity"]    += int(order.get("quantity", 0))
            stats[pid]["revenue"]     += int(order.get("totalPaymentAmount", 0))

        total_pages = body.get("data", {}).get("totalPages", 1)
        if page >= total_pages:
            break
        page += 1


def get_channel_product_detail(channel_product_no: str) -> dict:
    """채널 상품 상세 조회 (GET /v2/products/channel-products/{no})"""
    res = httpx.get(
        f"{_BASE}/external/v2/products/channel-products/{channel_product_no}",
        headers=_auth_headers(),
        timeout=15,
    )
    res.raise_for_status()
    return res.json()
