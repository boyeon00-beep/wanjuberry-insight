import base64
import hashlib
import hmac
import json
import os
import time
from urllib.parse import quote

import httpx

_BASE = "https://api.searchad.naver.com"


def _sign(timestamp: str, method: str, path: str) -> str:
    secret  = os.environ["NAVER_AD_SECRET_KEY"].encode("utf-8")
    message = f"{timestamp}.{method.upper()}.{path}".encode("utf-8")
    return base64.b64encode(hmac.new(secret, message, hashlib.sha256).digest()).decode("utf-8")


def _headers(sign_path: str) -> dict:
    timestamp = str(int(time.time() * 1000))
    return {
        "X-Timestamp": timestamp,
        "X-API-KEY":   os.environ["NAVER_AD_ACCESS_LICENSE"],
        "X-Customer":  os.environ["NAVER_AD_CUSTOMER_ID"],
        "X-Signature": _sign(timestamp, "GET", sign_path),
    }


def _get_simple(path_with_query: str) -> dict | list:
    """쿼리 파라미터 포함 GET — base path만 서명"""
    base_path = path_with_query.split("?")[0]
    res = httpx.get(
        f"{_BASE}{path_with_query}",
        headers=_headers(base_path),
        timeout=15,
    )
    res.raise_for_status()
    return res.json()


def _get_stats(ids: list[str], fields: list[str], start_date: str, end_date: str) -> list[dict]:
    """stats 엔드포인트 — base path만 서명, quote로 직접 URL 구성"""
    ids_str         = ",".join(ids)
    fields_str      = quote(json.dumps(fields, separators=(',', ':')))
    time_range_str  = quote(json.dumps({"since": start_date, "until": end_date}, separators=(',', ':')))
    query = f"ids={ids_str}&fields={fields_str}&timeRange={time_range_str}&timeUnit=date&breakdown=noBreakdown"
    res = httpx.get(f"{_BASE}/stats?{query}", headers=_headers("/stats"), timeout=20)
    res.raise_for_status()
    return res.json().get("data", [])


def get_campaigns() -> list[dict]:
    """활성 캠페인 목록 조회"""
    return _get_simple("/ncc/campaigns")


def get_adgroups(campaign_id: str) -> list[dict]:
    """캠페인 하위 광고그룹 목록 조회"""
    return _get_simple(f"/ncc/adgroups?nccCampaignId={campaign_id}")


def get_keywords(adgroup_id: str) -> list[dict]:
    """광고그룹 하위 키워드 목록 조회"""
    return _get_simple(f"/ncc/keywords?nccAdgroupId={adgroup_id}")


def get_campaign_stats(campaign_ids: list[str], start_date: str, end_date: str) -> list[dict]:
    """캠페인 성과 통계 조회. start_date / end_date: "YYYY-MM-DD" 형식"""
    return _get_stats(
        campaign_ids,
        ["impCnt", "clkCnt", "salesAmt", "ctr", "cpc", "convAmt"],
        start_date, end_date,
    )


def get_keyword_stats(keyword_ids: list[str], start_date: str, end_date: str) -> list[dict]:
    """키워드 성과 통계 조회"""
    return _get_stats(
        keyword_ids,
        ["impCnt", "clkCnt", "salesAmt", "ctr", "cpc", "convAmt", "avgRnk"],
        start_date, end_date,
    )
