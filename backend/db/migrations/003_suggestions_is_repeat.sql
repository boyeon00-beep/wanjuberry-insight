-- Phase 4-3: is_repeat 필드 추가 (거절/만료 이력이 있는 재제안 태깅)

ALTER TABLE suggestions ADD COLUMN IF NOT EXISTS is_repeat BOOLEAN DEFAULT FALSE;
