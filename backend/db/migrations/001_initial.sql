-- 완주베리 AI 운영 인사이트 — 초기 테이블 생성
-- Supabase SQL Editor에서 실행

-- 분석 실행 이력
CREATE TABLE IF NOT EXISTS analysis_runs (
    task_id       TEXT PRIMARY KEY,
    started_at    TIMESTAMPTZ NOT NULL,
    completed_at  TIMESTAMPTZ,
    season_flag   TEXT NOT NULL,
    season_note   TEXT,
    status        TEXT NOT NULL DEFAULT 'running',  -- running | success | error
    error         TEXT
);

-- 수집 상품 (네이버 커머스 · 쿠팡)
CREATE TABLE IF NOT EXISTS collected_products (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id             TEXT NOT NULL REFERENCES analysis_runs(task_id),
    product_id          TEXT NOT NULL,
    platform            TEXT NOT NULL,  -- naver | coupang
    name                TEXT NOT NULL,
    price               NUMERIC NOT NULL,
    sales_count         INT NOT NULL DEFAULT 0,
    review_count        INT NOT NULL DEFAULT 0,
    review_score        NUMERIC NOT NULL DEFAULT 0,
    category            TEXT,
    tags                TEXT[]    DEFAULT '{}',
    product_type        TEXT,     -- 생과 | 냉동 | 즙 | 가공품
    weight_kg           NUMERIC,
    unit_price_per_kg   NUMERIC,
    season_flag         TEXT,
    options             JSONB     DEFAULT '[]',
    collected_at        TIMESTAMPTZ NOT NULL
);

-- AI 제안함
CREATE TABLE IF NOT EXISTS suggestions (
    suggestion_id   UUID PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES analysis_runs(task_id),
    agent           TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    target_name     TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    current_value   TEXT,
    proposed_value  TEXT,
    reason          TEXT,
    priority        TEXT NOT NULL,  -- high | medium | low
    execution_tier  TEXT NOT NULL,  -- ai_auto | operator_manual | ai_after_approval
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected | expired
    created_at      TIMESTAMPTZ NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL
);

-- 실행 로그
CREATE TABLE IF NOT EXISTS action_logs (
    log_id          UUID PRIMARY KEY,
    suggestion_id   UUID NOT NULL REFERENCES suggestions(suggestion_id),
    task_id         TEXT NOT NULL,
    agent           TEXT NOT NULL,
    action_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    target_name     TEXT NOT NULL,
    execution_tier  TEXT NOT NULL,
    status          TEXT NOT NULL,  -- success | skipped | failed
    detail          TEXT,
    executed_at     TIMESTAMPTZ NOT NULL
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_suggestions_status   ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_task_id  ON suggestions(task_id);
CREATE INDEX IF NOT EXISTS idx_action_logs_task_id  ON action_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_collected_products_task ON collected_products(task_id);
