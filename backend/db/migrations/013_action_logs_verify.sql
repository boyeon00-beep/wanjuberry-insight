-- 실행 결과 반영 여부 검증 컬럼
alter table action_logs
  add column if not exists verify_status text
    check (verify_status in ('matched', 'not_matched', 'coupang_reviewing', 'error')),
  add column if not exists verified_at   timestamptz;
