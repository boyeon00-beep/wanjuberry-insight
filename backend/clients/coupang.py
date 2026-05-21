import hashlib
import hmac
import os
import time
from datetime import date, timedelta

import httpx

_BASE = "https://api-gateway.coupang.com"


def _hmac_header(method: str, path: str, query: str = "") -> dict:
    access_key = os.environ["COUPANG_ACCESS_KEY"]
    secret_key  = os.environ["COUPANG_SECRET_KEY"]

    # GMT+0 기준 yyMMddTHHmmssZ — 로컬 타임 사용 금지
    datetime_str = time.strftime("%y%m%dT%H%M%SZ", time.gmtime())
    message      = f"{datetime_str}{method}{path}{query}"
    signature    = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    auth = (
        f"CEA algorithm=HmacSHA256, "
        f"access-key={access_key}, "
        f"signed-date={datetime_str}, "
        f"signature={signature}"
    )
    return {"Authorization": auth}


def _put(path: str) -> dict:
    """body 없는 PUT (가격변경, 판매재개 등)."""
    headers = _hmac_header("PUT", path)
    res = httpx.put(f"{_BASE}{path}", headers=headers, timeout=20)
    if not res.is_success:
        raise RuntimeError(f"Coupang API {res.status_code}: {res.text[:500]}")
    return res.json()


def _get(path: str, params: dict) -> dict:
    # query string을 직접 조립해 서명과 실제 요청이 동일한 문자열 사용
    query = "&".join(f"{k}={v}" for k, v in params.items())
    headers = _hmac_header("GET", path, query)
    res = httpx.get(
        f"{_BASE}{path}?{query}",
        headers=headers,
        timeout=20,
    )
    if not res.is_success:
        raise RuntimeError(
            f"Coupang API {res.status_code}: {res.text[:500]}"
        )
    return res.json()


def update_price(vendor_item_id: str, price: int) -> dict:
    """vendorItemId 단위 판매가 변경. price는 10원 단위."""
    path = f"/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendor_item_id}/prices/{price}"
    result = _put(path)
    if result.get("code") == "ERROR":
        raise RuntimeError(f"가격 변경 실패: {result.get('message')}")
    return result


def resume_sale(vendor_item_id: str) -> dict:
    """vendorItemId 단위 판매 재개."""
    path = f"/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendor_item_id}/sales/resume"
    result = _put(path)
    if result.get("code") == "ERROR":
        raise RuntimeError(f"판매 재개 실패: {result.get('message')}")
    return result


def get_products() -> list[dict]:
    """APPROVED 상품 목록 전체 (cursor 페이지네이션)"""
    vendor_id = os.environ["COUPANG_VENDOR_ID"]
    path      = "/v2/providers/seller_api/apis/api/v1/marketplace/seller-products"

    products   = []
    next_token = ""

    while True:
        params: dict = {"vendorId": vendor_id, "maxPerPage": 100, "status": "APPROVED"}
        if next_token:
            params["nextToken"] = next_token

        body = _get(path, params)
        data = body.get("data", [])
        products.extend(data)

        next_token = body.get("nextToken", "")
        if not next_token:
            break

    return products


def get_revenue_history(days: int = 30) -> list[dict]:
    """매출내역 조회 (최대 31일, 종료일=어제, cursor 페이지네이션)

    반환: order 단위 리스트. 각 order는 saleType(SALE|REFUND) + items[] 포함.
    """
    vendor_id = os.environ["COUPANG_VENDOR_ID"]
    path      = "/v2/providers/openapi/apis/api/v1/revenue-history"

    today     = date.today()
    date_to   = today - timedelta(days=1)               # 어제까지만
    date_from = today - timedelta(days=min(days, 31))

    all_orders = []
    token      = ""  # 첫 페이지는 빈값 필수

    while True:
        params = {
            "vendorId":            vendor_id,
            "recognitionDateFrom": date_from.strftime("%Y-%m-%d"),
            "recognitionDateTo":   date_to.strftime("%Y-%m-%d"),
            "token":               token,
            "maxPerPage":          50,
        }

        body = _get(path, params)
        all_orders.extend(body.get("data", []))

        if not body.get("hasNext", False):
            break
        token = body.get("nextToken", "")

    return all_orders
