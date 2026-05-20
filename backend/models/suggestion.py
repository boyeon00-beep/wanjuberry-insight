from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
import uuid

from pydantic import BaseModel, Field


RejectionTag = Literal[
    "시즌맞지않음",
    "이미시도해봤음",
    "방향이다름",
    "여력없음",
    "기타",
]

ActionType = Literal[
    "상품명_수정",
    "태그_추가",
    "태그_수정",
    "재입고_제안",
    "가격_검토",
    "이미지_교체",
    "카피_수정",
    "키워드_추가",
    "키워드_제외",
    "입찰가_조정",
    "예산_조정",
    "예산_증액",
    "캠페인_일시중지",
]

ExecutionTier = Literal["ai_auto", "operator_manual", "ai_after_approval"]
SuggestionStatus = Literal["pending", "approved", "rejected", "expired"]


class Suggestion(BaseModel):
    suggestion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    agent: str
    target_id: str
    target_name: str
    action_type: ActionType
    current_value: str
    proposed_value: str
    reason: str
    priority: Literal["high", "medium", "low"]
    execution_tier: ExecutionTier
    status: SuggestionStatus = "pending"
    is_repeat: bool = False
    rejection_tag: Optional[RejectionTag] = None
    validator_verdict: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at: str = Field(
        default_factory=lambda: (
            datetime.now(timezone.utc) + timedelta(hours=72)
        ).isoformat()
    )
