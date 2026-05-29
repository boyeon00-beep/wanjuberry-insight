"""실행 완료된 ai_auto 제안의 실제 반영 여부 검증"""

import re

import store


async def verify_action_log(log_id: str) -> str:
    """
    반환: "matched" | "not_matched" | "coupang_reviewing" | "error"
    - matched:           실제로 반영됨
    - not_matched:       아직 미반영 (네이버)
    - coupang_reviewing: 쿠팡 내부 검토 중
    - error:             API 오류 또는 검증 불가
    """
    log = store.get_action_log(log_id)
    if not log or log.get("execution_tier") != "ai_auto" or log.get("status") != "success":
        return "error"

    # proposed_value는 suggestion에서 조회
    suggestion = store.get_suggestion(log["suggestion_id"])
    if not suggestion:
        return "error"

    action_type    = log["action_type"]
    agent          = log["agent"]
    target_id      = log["target_id"]
    target_name    = log.get("target_name", "")
    proposed_value = suggestion.get("proposed_value", "")

    try:
        if agent == "product_analyzer":
            return _verify_naver_product(action_type, target_id, proposed_value)
        if agent == "ad_analyzer":
            return _verify_naver_ad(action_type, target_id, proposed_value, target_name)
        if agent in ("coupang_analyzer", "coupang"):
            return _verify_coupang(action_type, target_id, proposed_value)
    except Exception:
        return "error"

    return "error"


# ── 네이버 커머스 상품 ──────────────────────────────────────────────────────

def _verify_naver_product(action_type: str, target_id: str, proposed_value: str) -> str:
    from clients import naver_commerce as client

    channel_no = client.find_channel_product_no(target_id)
    if not channel_no:
        return "error"

    body = client.get_channel_product_detail(channel_no)

    if action_type == "상품명_수정":
        current_name = body.get("name", "")
        expected = _parse_proposed_name(proposed_value)
        return "matched" if current_name == expected else "not_matched"

    if action_type in ("태그_추가", "태그_수정"):
        current_tags = {t.get("text", "") for t in (body.get("sellerTags") or [])}
        expected_tags = {t.strip().strip("'\"") for t in proposed_value.split(",") if t.strip()}
        if action_type == "태그_추가":
            return "matched" if expected_tags.issubset(current_tags) else "not_matched"
        return "matched" if expected_tags == current_tags else "not_matched"

    return "error"


# ── 네이버 검색광고 ────────────────────────────────────────────────────────

def _verify_naver_ad(action_type: str, target_id: str, proposed_value: str, target_name: str) -> str:
    from clients import naver_ad as client

    if action_type == "입찰가_조정":
        expected_bid = _parse_number(proposed_value)
        if expected_bid is None:
            return "error"
        for c in client.get_campaigns():
            for ag in client.get_adgroups(c["nccCampaignId"]):
                for kw in client.get_keywords(ag["nccAdgroupId"]):
                    if kw.get("nccKeywordId") == target_id or kw.get("keyword") == target_name:
                        return "matched" if int(kw.get("bidAmt", 0)) == expected_bid else "not_matched"
        return "error"

    if action_type in ("예산_조정", "예산_증액"):
        expected_budget = _parse_number(proposed_value)
        if expected_budget is None:
            return "error"
        for c in client.get_campaigns():
            if c["nccCampaignId"] == target_id:
                return "matched" if int(c.get("dailyBudget", 0)) == expected_budget else "not_matched"
        return "error"

    if action_type == "키워드_추가":
        keyword, _ = _parse_keyword_and_bid(proposed_value)
        for c in client.get_campaigns():
            if c["nccCampaignId"] == target_id:
                for ag in client.get_adgroups(target_id):
                    for kw in client.get_keywords(ag["nccAdgroupId"]):
                        if kw.get("keyword") == keyword:
                            return "matched"
                return "not_matched"
        return "error"

    if action_type == "카피_수정":
        h_m = re.search(r"(?:headline|헤드라인)\s*[:：]\s*['\"]?([^'\",\n/]+)['\"]?", proposed_value, re.IGNORECASE)
        expected_headline = h_m.group(1).strip() if h_m else proposed_value.strip().strip("'\"")[:15]
        for c in client.get_campaigns():
            for ag in client.get_adgroups(c["nccCampaignId"]):
                for ad in client.get_ads(ag["nccAdgroupId"]):
                    if ad.get("nccAdId") == target_id:
                        return "matched" if ad.get("headline", "").strip() == expected_headline else "not_matched"
        return "error"

    return "error"


# ── 쿠팡 ──────────────────────────────────────────────────────────────────

def _verify_coupang(action_type: str, target_id: str, proposed_value: str) -> str:
    from clients import coupang as client

    product = client.get_product_detail(target_id)

    if action_type == "상품명_수정":
        current_name = product.get("sellerProductName", "")
        expected = _parse_proposed_name(proposed_value)
        return "matched" if current_name == expected else "coupang_reviewing"

    if action_type in ("태그_추가", "태그_수정"):
        items = product.get("items", [])
        current_tags = set((items[0].get("searchTags") or []) if items else [])
        expected_tags = {t.strip() for t in proposed_value.replace("'", "").replace('"', "").split(",") if t.strip()}
        if action_type == "태그_추가":
            matched = expected_tags.issubset(current_tags)
        else:
            matched = expected_tags == current_tags
        return "matched" if matched else "coupang_reviewing"

    if action_type == "가격_검토":
        items = product.get("items", [])
        prices = [int(item.get("salePrice", 0)) for item in items if item.get("salePrice")]
        if not prices:
            return "error"
        expected_price = _parse_number(proposed_value)
        if expected_price is None:
            return "error"
        return "matched" if min(prices) == expected_price else "not_matched"

    return "error"


# ── 헬퍼 ──────────────────────────────────────────────────────────────────

def _parse_proposed_name(proposed_value: str) -> str:
    """'상품명' (32자) 형태에서 순수 상품명만 추출"""
    text = re.sub(r'\s*\(\d+자\)\s*$', '', proposed_value.strip())
    return text.strip().strip("'\"").strip()


def _parse_number(text: str) -> int | None:
    m = re.search(r"[\d,]+", text.replace(" ", ""))
    return int(m.group().replace(",", "")) if m else None


def _parse_keyword_and_bid(text: str) -> tuple[str, int | None]:
    m = re.match(r"^([^:]+?)(?:\s*[:：]\s*([\d,]+)원?)?$", text.strip())
    if m:
        keyword = m.group(1).strip().strip("'\"")
        bid_str = m.group(2)
        return keyword, (int(bid_str.replace(",", "")) if bid_str else None)
    return text.strip().strip("'\""), None
