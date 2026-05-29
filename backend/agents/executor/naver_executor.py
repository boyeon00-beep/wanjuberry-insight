"""네이버 제안 실행 — 검색광고(6종) + 커머스 상품(3종) 실제 API 호출"""

import re

import store
from models.action_log import ActionLog
from models.suggestion import Suggestion


async def execute_naver(
    suggestion: Suggestion,
    baseline_metrics: dict | None = None,
    ad_strategy_mode: str | None = None,
) -> ActionLog:
    t = suggestion.action_type

    # 검색광고
    if t == "입찰가_조정":
        return _execute_keyword_bid(suggestion, baseline_metrics, ad_strategy_mode)
    if t == "키워드_추가":
        return _execute_keyword_add(suggestion, baseline_metrics, ad_strategy_mode)
    if t == "키워드_제외":
        return _execute_keyword_exclude(suggestion, baseline_metrics, ad_strategy_mode)
    if t in ("예산_조정", "예산_증액"):
        return _execute_budget_update(suggestion, baseline_metrics, ad_strategy_mode)
    if t == "캠페인_일시중지":
        return _execute_campaign_pause(suggestion, baseline_metrics, ad_strategy_mode)
    if t == "카피_수정":
        return _execute_ad_copy(suggestion, baseline_metrics, ad_strategy_mode)

    # 커머스 상품
    if t == "상품명_수정":
        return _execute_product_name(suggestion, baseline_metrics, ad_strategy_mode)
    if t in ("태그_추가", "태그_수정"):
        return _execute_product_tags(suggestion, baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "skipped",
        f"미구현 action_type: {t}",
        baseline_metrics, ad_strategy_mode,
    )


# ──────────────────────────────── 검색광고 ────────────────────────────────

def _execute_keyword_bid(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    bid = _parse_number(suggestion.proposed_value)
    if bid is None:
        return _make_log(suggestion, "failed", f"입찰가 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    keyword_id = _find_keyword_id(suggestion.target_id, suggestion.target_name, client)
    if not keyword_id:
        return _make_log(suggestion, "failed", f"키워드 ID 조회 실패: {suggestion.target_name}", baseline_metrics, ad_strategy_mode)

    try:
        client.update_keyword_bid(keyword_id, bid)
    except Exception as e:
        return _make_log(suggestion, "failed", f"입찰가 변경 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"입찰가 변경 완료 ({bid:,}원) — 키워드: {suggestion.target_name}",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


def _execute_keyword_add(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    # proposed_value: "복분자구매: 150원" 또는 "복분자구매"
    keyword, bid = _parse_keyword_and_bid(suggestion.proposed_value)
    if not keyword:
        keyword = suggestion.target_name  # fallback

    campaign_id = suggestion.target_id
    adgroup_id = _find_first_adgroup(campaign_id, client)
    if not adgroup_id:
        return _make_log(suggestion, "failed", f"광고그룹 조회 실패 (캠페인: {campaign_id})", baseline_metrics, ad_strategy_mode)

    try:
        client.add_keyword(adgroup_id, keyword, bid)
    except Exception as e:
        return _make_log(suggestion, "failed", f"키워드 추가 실패: {e}", baseline_metrics, ad_strategy_mode)

    detail = f"키워드 추가 완료 — '{keyword}'"
    if bid:
        detail += f" (입찰가: {bid:,}원)"
    return _make_log(suggestion, "success", detail, baseline_metrics, ad_strategy_mode, effect_verdict="pending")


def _execute_keyword_exclude(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    # 제외할 키워드 텍스트 결정
    keyword = suggestion.target_name or _parse_keyword_text(suggestion.proposed_value)
    campaign_id = suggestion.target_id

    # 키워드의 adgroup_id 조회
    adgroup_id = _find_keyword_adgroup(campaign_id, keyword, client)
    if not adgroup_id:
        adgroup_id = _find_first_adgroup(campaign_id, client)
    if not adgroup_id:
        return _make_log(suggestion, "failed", f"광고그룹 조회 실패 (캠페인: {campaign_id})", baseline_metrics, ad_strategy_mode)

    try:
        client.add_negative_keyword(adgroup_id, keyword)
    except Exception as e:
        return _make_log(suggestion, "failed", f"키워드 제외 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"키워드 제외 완료 — '{keyword}'",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


def _execute_budget_update(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    budget = _parse_number(suggestion.proposed_value)
    if budget is None:
        return _make_log(suggestion, "failed", f"예산 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    campaign_id = suggestion.target_id
    try:
        client.update_campaign(campaign_id, {"dailyBudget": budget})
    except Exception as e:
        return _make_log(suggestion, "failed", f"예산 변경 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"일일예산 변경 완료 ({budget:,}원) — {suggestion.target_name}",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


def _execute_campaign_pause(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    campaign_id = suggestion.target_id
    try:
        client.pause_campaign(campaign_id)
    except Exception as e:
        return _make_log(suggestion, "failed", f"캠페인 일시중지 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"캠페인 일시중지 완료 — {suggestion.target_name}",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


def _execute_ad_copy(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_ad as client

    ad_id = suggestion.target_id  # nccAdId

    # 전체 광고 목록에서 해당 ad 오브젝트 조회
    try:
        ad_obj, adgroup_id = _find_ad_object(ad_id, client)
    except Exception as e:
        return _make_log(suggestion, "failed", f"광고 소재 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    if not ad_obj:
        return _make_log(suggestion, "failed", f"광고 ID 없음: {ad_id}", baseline_metrics, ad_strategy_mode)

    # proposed_value에서 새 카피 파싱
    new_headline, new_desc1, new_desc2 = _parse_ad_copy(suggestion.proposed_value)
    if not new_headline:
        return _make_log(suggestion, "failed", f"카피 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    # 기존 ad 오브젝트에 수정 반영
    updated = dict(ad_obj)
    ad_attr = dict(updated.get("adAttr") or {})
    if new_headline:
        updated["headline"] = new_headline
        ad_attr["headline"] = new_headline
    if new_desc1:
        updated["description"] = new_desc1
        ad_attr["description"] = new_desc1
    if new_desc2:
        updated["description2"] = new_desc2
        ad_attr["description2"] = new_desc2
    updated["adAttr"] = ad_attr

    try:
        client.update_ad(ad_id, adgroup_id, updated)
    except Exception as e:
        return _make_log(suggestion, "failed", f"광고 소재 수정 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"광고 소재 수정 완료 — headline: '{new_headline}'",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


# ──────────────────────────────── 커머스 상품 ────────────────────────────────

def _execute_product_name(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_commerce as client

    import re as _re
    _raw = (suggestion.proposed_value or "").strip()
    _raw = _re.sub(r'\s*\(\d+자\)\s*$', '', _raw)  # "(32자)" 제거
    new_name = _raw.strip().strip("'\"").strip()
    if not new_name:
        return _make_log(suggestion, "failed", f"상품명 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    try:
        channel_no = client.find_channel_product_no(suggestion.target_id)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    if not channel_no:
        return _make_log(suggestion, "failed", f"채널상품 없음 (target_id: {suggestion.target_id})", baseline_metrics, ad_strategy_mode)

    try:
        body = client.get_channel_product_detail(channel_no)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 상세 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    old_name = body.get("name", "")
    body["name"] = new_name

    try:
        client.update_channel_product(channel_no, body)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품명 수정 실패: {e}", baseline_metrics, ad_strategy_mode)

    return _make_log(
        suggestion, "success",
        f"상품명 수정 완료 — '{old_name}' → '{new_name}'",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


def _execute_product_tags(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import naver_commerce as client

    # proposed_value: "복분자, 냉동복분자, 완주베리" 형태
    new_tags = [t.strip().strip("'\"") for t in suggestion.proposed_value.split(",") if t.strip()]
    if not new_tags:
        return _make_log(suggestion, "failed", f"태그 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    try:
        channel_no = client.find_channel_product_no(suggestion.target_id)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    if not channel_no:
        return _make_log(suggestion, "failed", f"채널상품 없음 (target_id: {suggestion.target_id})", baseline_metrics, ad_strategy_mode)

    try:
        body = client.get_channel_product_detail(channel_no)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 상세 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    if suggestion.action_type == "태그_추가":
        existing = [t.get("text", "") for t in (body.get("sellerTags") or [])]
        merged = list(dict.fromkeys(existing + new_tags))  # 중복 제거, 순서 유지
        body["sellerTags"] = [{"text": t} for t in merged]
    else:  # 태그_수정 — 전체 교체
        body["sellerTags"] = [{"text": t} for t in new_tags]

    try:
        client.update_channel_product(channel_no, body)
    except Exception as e:
        return _make_log(suggestion, "failed", f"태그 수정 실패: {e}", baseline_metrics, ad_strategy_mode)

    action_label = "추가" if suggestion.action_type == "태그_추가" else "교체"
    return _make_log(
        suggestion, "success",
        f"판매자 태그 {action_label} 완료 — {new_tags}",
        baseline_metrics, ad_strategy_mode, effect_verdict="pending",
    )


# ──────────────────────────────── 헬퍼 ────────────────────────────────

def _find_keyword_id(target_id: str, keyword_text: str, client) -> str | None:
    """target_id가 nkw- 형식이면 직접 반환, 아니면 캠페인 스캔으로 검색"""
    if target_id.startswith("nkw-"):
        return target_id

    try:
        campaigns = client.get_campaigns()
        for c in campaigns:
            adgroups = client.get_adgroups(c["nccCampaignId"])
            for ag in adgroups:
                kws = client.get_keywords(ag["nccAdgroupId"])
                for kw in kws:
                    if kw.get("keyword", "") == keyword_text:
                        return kw["nccKeywordId"]
    except Exception:
        pass
    return None


def _find_keyword_adgroup(campaign_id: str, keyword_text: str, client) -> str | None:
    """키워드 텍스트로 adgroup_id 조회"""
    try:
        adgroups = client.get_adgroups(campaign_id)
        for ag in adgroups:
            ag_id = ag["nccAdgroupId"]
            kws = client.get_keywords(ag_id)
            for kw in kws:
                if kw.get("keyword", "") == keyword_text:
                    return ag_id
    except Exception:
        pass
    return None


def _find_first_adgroup(campaign_id: str, client) -> str | None:
    """캠페인의 첫 번째 광고그룹 ID 반환"""
    try:
        adgroups = client.get_adgroups(campaign_id)
        if adgroups:
            return adgroups[0]["nccAdgroupId"]
    except Exception:
        pass
    return None


def _find_ad_object(ad_id: str, client) -> tuple[dict | None, str]:
    """전체 캠페인 스캔으로 ad 오브젝트 및 adgroup_id 반환"""
    campaigns = client.get_campaigns()
    for c in campaigns:
        adgroups = client.get_adgroups(c["nccCampaignId"])
        for ag in adgroups:
            ag_id = ag["nccAdgroupId"]
            ads = client.get_ads(ag_id)
            for ad in ads:
                if ad.get("nccAdId") == ad_id:
                    return ad, ag_id
    return None, ""


def _parse_number(text: str) -> int | None:
    """텍스트에서 첫 번째 숫자(콤마 허용) 추출 → int"""
    m = re.search(r"[\d,]+", text.replace(" ", ""))
    if m:
        return int(m.group().replace(",", ""))
    return None


def _parse_keyword_and_bid(text: str) -> tuple[str, int | None]:
    """'복분자구매: 150원' 또는 '복분자구매' 형태에서 (keyword, bid) 파싱"""
    m = re.match(r"^([^:]+?)(?:\s*[:：]\s*([\d,]+)원?)?$", text.strip())
    if m:
        keyword = m.group(1).strip().strip("'\"")
        bid_str = m.group(2)
        bid = int(bid_str.replace(",", "")) if bid_str else None
        return keyword, bid
    return text.strip().strip("'\""), None


def _parse_keyword_text(text: str) -> str:
    """제안 내용에서 키워드 텍스트만 추출"""
    # "제외 키워드: 복분자" 또는 그냥 "복분자" 형태 모두 처리
    m = re.search(r"['\"](.+?)['\"]", text)
    if m:
        return m.group(1)
    return text.strip().split(":")[0].strip()


def _parse_ad_copy(text: str) -> tuple[str, str, str]:
    """proposed_value에서 (headline, description1, description2) 파싱.

    지원 형식:
      "headline: 'xxx', description1: 'yyy'"
      "헤드라인: xxx / 설명: yyy"
      단순 텍스트 → headline에만 배정
    """
    # headline 패턴
    h_m = re.search(r"(?:headline|헤드라인)\s*[:：]\s*['\"]?([^'\",\n/]+)['\"]?", text, re.IGNORECASE)
    d1_m = re.search(r"(?:description1?|설명1?|desc1?)\s*[:：]\s*['\"]?([^'\",\n/]+)['\"]?", text, re.IGNORECASE)
    d2_m = re.search(r"(?:description2|설명2|desc2)\s*[:：]\s*['\"]?([^'\",\n/]+)['\"]?", text, re.IGNORECASE)

    headline = h_m.group(1).strip() if h_m else text.strip().strip("'\"")[:15]
    desc1    = d1_m.group(1).strip() if d1_m else ""
    desc2    = d2_m.group(1).strip() if d2_m else ""
    return headline, desc1, desc2


def _make_log(
    suggestion: Suggestion,
    status: str,
    detail: str,
    baseline_metrics,
    ad_strategy_mode,
    effect_verdict=None,
) -> ActionLog:
    log = ActionLog(
        suggestion_id=suggestion.suggestion_id,
        task_id=suggestion.task_id,
        agent="executor",
        action_type=suggestion.action_type,
        target_id=suggestion.target_id,
        target_name=suggestion.target_name,
        execution_tier=suggestion.execution_tier,
        status=status,
        detail=detail,
        baseline_metrics=baseline_metrics,
        effect_verdict=effect_verdict,
        ad_strategy_mode=ad_strategy_mode,
    )
    store.add_action_log(log)
    return log
