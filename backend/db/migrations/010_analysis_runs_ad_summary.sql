-- 광고 캠페인 성과 데이터 저장 (분석 실행 시 collect 단계 결과)
ALTER TABLE analysis_runs
ADD COLUMN IF NOT EXISTS ad_summary JSONB DEFAULT NULL;
