from datetime import datetime, timezone
from typing import Literal, Optional
import uuid

from pydantic import BaseModel, Field

from models.suggestion import ActionType, ExecutionTier


ActionLogStatus = Literal["success", "skipped", "failed", "rejected"]

# effect_verdict: pending → 측정 대기 / positive·neutral·negative → 측정 완료 / unmeasurable → 측정 불가
EffectVerdict = Literal["pending", "positive", "neutral", "negative", "unmeasurable"]

# verify_status: 실제 반영 여부 검증 결과
VerifyStatus = Literal["matched", "not_matched", "coupang_reviewing", "error"]


class ActionLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    suggestion_id: str
    task_id: str
    agent: str
    action_type: ActionType
    target_id: str
    target_name: str
    execution_tier: ExecutionTier
    status: ActionLogStatus
    detail: str
    executed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    baseline_metrics: Optional[dict] = None
    result_metrics: Optional[dict] = None
    effect_verdict: Optional[EffectVerdict] = None
    effect_measured_at: Optional[str] = None
    ad_strategy_mode: Optional[str] = None
    verify_status: Optional[VerifyStatus] = None
    verified_at: Optional[str] = None
