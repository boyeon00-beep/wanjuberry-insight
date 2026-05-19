from datetime import datetime, timezone
from typing import Literal
import uuid

from pydantic import BaseModel, Field

from models.suggestion import ActionType, ExecutionTier


ActionLogStatus = Literal["success", "skipped", "failed", "rejected"]


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
