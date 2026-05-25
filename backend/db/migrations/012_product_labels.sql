-- 상품별 베리 분류 라벨 (운영자 직접 지정, 수집과 독립적으로 영구 보존)
CREATE TABLE IF NOT EXISTS product_labels (
  product_id   TEXT PRIMARY KEY,
  product_name TEXT,
  platform     TEXT NOT NULL DEFAULT 'naver',
  berry_type   TEXT CHECK (berry_type IN ('복분자', '블랙베리', '복분자+블랙베리', '기타')),
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);
