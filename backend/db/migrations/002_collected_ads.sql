-- Phase 4-3: 광고 소재 수집 테이블

CREATE TABLE IF NOT EXISTS collected_ads (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id      TEXT NOT NULL REFERENCES analysis_runs(task_id),
    ad_id        TEXT NOT NULL,
    adgroup_id   TEXT NOT NULL,
    campaign_id  TEXT NOT NULL,
    headline     TEXT,
    description1 TEXT,
    description2 TEXT,
    ad_type      TEXT,
    status       TEXT,
    collected_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_collected_ads_task ON collected_ads(task_id);
