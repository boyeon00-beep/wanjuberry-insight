-- 그룹상품 번호 컬럼 추가
-- 네이버 스마트스토어 그룹상품(여러 개별 상품을 하나로 묶은 표준형 그룹) 지원
-- 그룹에 속하지 않는 개별 상품은 빈 문자열('')

ALTER TABLE collected_products
  ADD COLUMN IF NOT EXISTS group_product_no TEXT NOT NULL DEFAULT '';
