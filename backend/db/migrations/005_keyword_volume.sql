CREATE TABLE IF NOT EXISTS keyword_volume (
  id             uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  task_id        text        NOT NULL,
  keyword        text        NOT NULL,
  monthly_pc     int         DEFAULT 0,
  monthly_mobile int         DEFAULT 0,
  monthly_total  int         DEFAULT 0,
  competition    text        DEFAULT '',
  is_bidding     boolean     DEFAULT false,
  collected_at   timestamptz DEFAULT now()
);
