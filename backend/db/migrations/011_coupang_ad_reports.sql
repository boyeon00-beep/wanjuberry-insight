-- collected_products에 vendor_item_ids 컬럼 추가
ALTER TABLE collected_products
  ADD COLUMN IF NOT EXISTS vendor_item_ids JSONB DEFAULT '[]'::jsonb;

-- Wing 광고 보고서 저장 테이블
CREATE TABLE IF NOT EXISTS coupang_ad_reports (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_at             TIMESTAMPTZ DEFAULT NOW(),
    report_from             DATE NOT NULL,
    report_to               DATE NOT NULL,
    vendor_item_id          TEXT NOT NULL,
    product_id              TEXT,                   -- 매핑된 sellerProductId (NULL 허용)
    product_name            TEXT,
    campaign_name           TEXT,
    adgroup_name            TEXT,
    impressions             INTEGER DEFAULT 0,
    clicks                  INTEGER DEFAULT 0,
    ad_cost                 INTEGER DEFAULT 0,
    orders_14d              INTEGER DEFAULT 0,
    conversion_revenue_14d  INTEGER DEFAULT 0,
    roas_14d                NUMERIC,                -- 광고비 0이면 NULL
    sales_qty_14d           INTEGER DEFAULT 0
);
