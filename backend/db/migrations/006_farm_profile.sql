CREATE TABLE IF NOT EXISTS farm_profile (
  id         int  PRIMARY KEY DEFAULT 1,
  content    text NOT NULL DEFAULT '',
  updated_at timestamptz DEFAULT now()
);
-- 항상 1개 행 유지
INSERT INTO farm_profile (id, content) VALUES (1, '') ON CONFLICT (id) DO NOTHING;
