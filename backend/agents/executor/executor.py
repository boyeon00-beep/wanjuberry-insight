# 단일 실행 에이전트 — 승인된 Suggestion을 받아 실행 후 ActionLog 기록

import store
from models.action_log import ActionLog
from models.suggestion import Suggestion


async def execute(
    suggestion: Suggestion,
    baseline_metrics: dict | None = None,
    ad_strategy_mode: str | None = None,
) -> ActionLog:
    if suggestion.execution_tier == "operator_manual":
        log = ActionLog(
            suggestion_id=suggestion.suggestion_id,
            task_id=suggestion.task_id,
            agent=suggestion.agent,
            action_type=suggestion.action_type,
            target_id=suggestion.target_id,
            target_name=suggestion.target_name,
            execution_tier=suggestion.execution_tier,
            status="skipped",
            detail=f"운영자 직접 실행 항목 — AI 실행 생략. 제안 내용: {suggestion.proposed_value}",
            baseline_metrics=baseline_metrics,
            ad_strategy_mode=ad_strategy_mode,
        )
        store.add_action_log(log)
        return log

    # 쿠팡 에이전트 — 실제 API 실행
    if suggestion.agent in ("coupang", "coupang_analyzer"):
        from agents.executor.coupang_executor import execute_coupang
        return await execute_coupang(suggestion, baseline_metrics, ad_strategy_mode)

    # 네이버 에이전트 — 실제 API 실행
    if suggestion.agent in ("ad_analyzer", "product_analyzer", "naver"):
        from agents.executor.naver_executor import execute_naver
        return await execute_naver(suggestion, baseline_metrics, ad_strategy_mode)

    # 미지원 에이전트
    log = ActionLog(
        suggestion_id=suggestion.suggestion_id,
        task_id=suggestion.task_id,
        agent=suggestion.agent,
        action_type=suggestion.action_type,
        target_id=suggestion.target_id,
        target_name=suggestion.target_name,
        execution_tier=suggestion.execution_tier,
        status="skipped",
        detail=f"미지원 에이전트: {suggestion.agent}",
        baseline_metrics=baseline_metrics,
        ad_strategy_mode=ad_strategy_mode,
    )
    store.add_action_log(log)
    return log
