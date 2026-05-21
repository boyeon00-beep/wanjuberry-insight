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

    # 상품명_수정 / 태그_추가 / 태그_수정: 쿠팡 전체 상품 수정은 API 승인 필요 → Wing 수동 안내
    return _make_log(
        suggestion,
        "skipped",
        f"쿠팡 Wing에서 직접 수정 필요 — {suggestion.proposed_value}",
        baseline_metrics,
        ad_strategy_mode,
    )


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
