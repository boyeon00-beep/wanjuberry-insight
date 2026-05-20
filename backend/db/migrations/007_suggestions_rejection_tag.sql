-- Phase 6-1: 거절 태그 컬럼 추가
ALTER TABLE suggestions
ADD COLUMN IF NOT EXISTS rejection_tag VARCHAR(20) DEFAULT NULL;
