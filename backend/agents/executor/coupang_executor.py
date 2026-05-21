import re

import store
from models.action_log import ActionLog
from models.suggestion import Suggestion


async def execute_coupang(
    suggestion: Suggestion,
    baseline_metrics: dict | None = None,
    ad_strategy_mode: str | None = None,
) -> ActionLog:
    """쿠팡 제안 실행. vendorItemId 기반 API 호출."""

    vendor_item_ids = store.get_product_vendor_item_ids(suggestion.target_id)

    if suggestion.action_type == "가격_검토":
        return _execute_price_update(suggestion, vendor_item_ids, baseline_metrics, ad_strategy_mode)

    if suggestion.action_type == "재입고_제안":
        return _execute_sale_resume(suggestion, vendor_item_ids, baseline_metrics, ad_strategy_mode)

    if suggestion.action_type == "상품명_수정":
        return _execute_name_update(suggestion, baseline_metrics, ad_strategy_mode)

    if suggestion.action_type in ("태그_추가", "태그_수정"):
        return _execute_tag_update(suggestion, baseline_metrics, ad_strategy_mode)

    return _make_log(suggestion, "skipped", f"미구현 action_type: {suggestion.action_type}", baseline_metrics, ad_strategy_mode)


def _execute_price_update(suggestion, vendor_item_ids, baseline_metrics, ad_strategy_mode):
    from clients import coupang as client

    if not vendor_item_ids:
        return _make_log(suggestion, "failed", "vendorItemId 없음 — 분석 후 재시도", baseline_metrics, ad_strategy_mode)

    price_match = re.search(r"[\d,]+", suggestion.proposed_value.replace(" ", ""))
    if not price_match:
        return _make_log(suggestion, "failed", f"가격 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    price = int(price_match.group().replace(",", ""))
    price = (price // 10) * 10  # 10원 단위 라운딩

    ok, fail = [], []
    for vid in vendor_item_ids:
        try:
            client.update_price(vid, price)
            ok.append(vid)
        except Exception as e:
            fail.append(f"{vid}:{e}")

    if fail and not ok:
        return _make_log(suggestion, "failed", f"가격 변경 실패 ({price:,}원): {fail}", baseline_metrics, ad_strategy_mode)

    detail = f"가격 변경 완료 ({price:,}원) — vendorItemId {ok}"
    if fail:
        detail += f" / 일부 실패: {fail}"
    return _make_log(suggestion, "success", detail, baseline_metrics, ad_strategy_mode, effect_verdict="pending")


def _execute_sale_resume(suggestion, vendor_item_ids, baseline_metrics, ad_strategy_mode):
    from clients import coupang as client

    if not vendor_item_ids:
        return _make_log(suggestion, "failed", "vendorItemId 없음 — 분석 후 재시도", baseline_metrics, ad_strategy_mode)

    ok, fail = [], []
    for vid in vendor_item_ids:
        try:
            client.resume_sale(vid)
            ok.append(vid)
        except Exception as e:
            fail.append(f"{vid}:{e}")

    if fail and not ok:
        return _make_log(suggestion, "failed", f"판매 재개 실패: {fail}", baseline_metrics, ad_strategy_mode)

    detail = f"판매 재개 완료 — vendorItemId {ok}"
    if fail:
        detail += f" / 일부 실패: {fail}"
    return _make_log(suggestion, "success", detail, baseline_metrics, ad_strategy_mode, effect_verdict="pending")


def _execute_name_update(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import coupang as client

    seller_product_id = suggestion.target_id
    new_name = suggestion.proposed_value.strip()

    try:
        product = client.get_product_detail(seller_product_id)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    old_name = product.get("sellerProductName", "")
    product["sellerProductName"] = new_name

    try:
        client.update_product(seller_product_id, product)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품명 변경 신청 실패: {e}", baseline_metrics, ad_strategy_mode)

    detail = f"상품명 변경 신청 완료 (쿠팡 승인 대기) — '{old_name}' → '{new_name}'"
    return _make_log(suggestion, "success", detail, baseline_metrics, ad_strategy_mode, effect_verdict="pending")


def _execute_tag_update(suggestion, baseline_metrics, ad_strategy_mode):
    from clients import coupang as client

    seller_product_id = suggestion.target_id
    # proposed_value: "복분자, 냉동복분자, 건강과일" 형태 파싱
    new_tags = [t.strip() for t in suggestion.proposed_value.replace("'", "").replace('"', "").split(",") if t.strip()]

    if not new_tags:
        return _make_log(suggestion, "failed", f"태그 파싱 실패: {suggestion.proposed_value}", baseline_metrics, ad_strategy_mode)

    try:
        product = client.get_product_detail(seller_product_id)
    except Exception as e:
        return _make_log(suggestion, "failed", f"상품 조회 실패: {e}", baseline_metrics, ad_strategy_mode)

    items = product.get("items", [])
    for item in items:
        if suggestion.action_type == "태그_추가":
            existing = item.get("searchTags") or []
            merged = list(dict.fromkeys(existing + new_tags))  # 중복 제거, 순서 유지
            item["searchTags"] = merged
        else:  # 태그_수정 — 전체 교체
            item["searchTags"] = new_tags

    try:
        client.update_product(seller_product_id, product)
    except Exception as e:
        return _make_log(suggestion, "failed", f"태그 변경 신청 실패: {e}", baseline_metrics, ad_strategy_mode)

    action_label = "추가" if suggestion.action_type == "태그_추가" else "교체"
    detail = f"검색태그 {action_label} 신청 완료 (쿠팡 승인 대기) — {new_tags}"
    return _make_log(suggestion, "success", detail, baseline_metrics, ad_strategy_mode, effect_verdict="pending")


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
