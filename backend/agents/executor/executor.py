# 단일 실행 에이전트 — 승인된 Suggestion을 받아 실행 후 ActionLog 기록
# Phase 2: 실제 API 호출 없이 mock 실행 (Phase 3에서 플랫폼 API 연결)

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
            agent="executor",
            action_type=suggestion.action_type,
            target_id=suggestion.target_id,
            target_name=suggestion.target_name,
            execution_tier=suggestion.execution_tier,
            status="skipped",
            detail=f"운영자 직접 실행 항목 — AI 실행 생략. 제안 내용: {suggestion.proposed_value}",
            baseline_metrics=baseline_metrics,
            ad_strategy_mode=ad_strategy_mode,
        )
    else:
        # ai_auto / ai_after_approval — Phase 2: mock 실행
        log = ActionLog(
            suggestion_id=suggestion.suggestion_id,
            task_id=suggestion.task_id,
            agent="executor",
            action_type=suggestion.action_type,
            target_id=suggestion.target_id,
            target_name=suggestion.target_name,
            execution_tier=suggestion.execution_tier,
            status="success",
            detail=f"[mock] {suggestion.action_type} 실행 완료. {suggestion.proposed_value}",
            baseline_metrics=baseline_metrics,
            effect_verdict="pending",
            ad_strategy_mode=ad_strategy_mode,
        )

    store.add_action_log(log)
    return log
