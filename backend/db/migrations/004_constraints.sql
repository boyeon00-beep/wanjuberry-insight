-- 농장 팩트 (운영자 확인 제약 조건) — AI 제안 생성 전 반드시 참조
CREATE TABLE IF NOT EXISTS constraints (
  id         uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  content    text        NOT NULL,
  source     text        DEFAULT 'manual',   -- 'manual' | 'rejection'
  created_at timestamptz DEFAULT now()
);
