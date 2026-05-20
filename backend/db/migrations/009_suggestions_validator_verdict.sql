-- Phase 6-5: Validator 판정 컬럼 추가
ALTER TABLE suggestions
ADD COLUMN IF NOT EXISTS validator_verdict VARCHAR(20) DEFAULT NULL;
