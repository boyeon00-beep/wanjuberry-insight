# 쿠팡 데이터 인벤토리

> 목적: 쿠팡에서 실제로 수집 가능한 데이터, 현재 DB에 저장되는 데이터, 프론트에서 보여줄 수 있는 데이터를 명확히 구분한다.
> 작성 기준: 2026-05-21, 현재 코드 직접 조사 기반

---

## 1. API 채널 구분

쿠팡 API는 두 채널로 나뉜다.

| 채널 | 역할 | 현재 상태 |
|---|---|---|
| **쿠팡 Open API** | 상품 목록, 주문/매출/정산 데이터 | 연결됨 (`backend/clients/coupang.py`) |
| **쿠팡 Wing API (셀러센터)** | 광고 데이터 (노출·클릭·전환·광고비) | 미연결 — 별도 인증/구현 필요 |

---

## 2. 데이터 인벤토리 표

| 데이터 항목 | 현재 수집 가능 여부 | 출처/API | 저장 위치 | 프론트 표시 여부 | 비고 |
|---|---|---|---|---|---|
| 쿠팡 상품명 | **가능** | Open API — 상품 목록 | collected_products.name | 가능 | `sellerProductName` |
| 판매 상태 | **가능** | Open API — 상품 목록 | — | 가능 | `statusName` (승인완료 등), APPROVED 필터 후 수집 |
| 가격 | **가능** | Open API — 매출 내역 | collected_products.price | 가능 | 단위 판매가 (`salePrice`) |
| 주문수 | **가능** | Open API — 매출 내역 (30일) | collected_products.sales_count | 가능 | SALE/REFUND 차감 후 집계 |
| 매출 | **가능** | Open API — 매출 내역 (30일) | collected_products.sales_revenue | 가능 | `saleAmount` 기준 (정산액 아님, 아래 확인필요 참조) |
| 정산금액 | **확인필요** | Open API — 매출 내역 | 미저장 | 불가 | `settlementAmount` 응답에 있지만 현재 코드는 `saleAmount` 사용 중 — 수수료 제외 실수령액이므로 확인 필요 |
| 서비스 수수료 | **가능(미저장)** | Open API — 매출 내역 | 미저장 | 불가 | `serviceFee`, `serviceFeeRatio` 응답에 있음, 현재 저장 안 함 |
| 배송비 | **가능(미저장)** | Open API — 매출 내역 | 미저장 | 불가 | `deliveryFee` 구조 응답에 있음, 배송 유형 구분은 확인필요 |
| 재고 상태 | **가능(미구현)** | Open API — vendor-item-inventory | 미저장 | 불가 | `vendorItemId`는 revenue-history에서 이미 수집됨 → 단건 조회 N회 호출로 연결 가능. 현재 `stock=0` 고정 |
| 옵션 정보 | **가능(미구현)** | Open API — vendor-item-inventory | 미저장 | 불가 | `vendorItemId`로 옵션별 재고·가격·판매상태 조회 가능. 현재 미구현 |
| 배송비/배송방법 | **가능(미구현)** | Open API — product-partial-get | 미저장 | 불가 | `deliveryCharge`, `deliveryChargeType`, `deliveryMethod`, 도서산간 여부 조회 가능 |
| 상품 이미지 | **불가** | — | — | 불가 | product-list-paged 응답에 이미지 URL 없음 — sample.json 직접 확인 완료 |
| 카테고리 | **가능(ID만)** | Open API — 상품 목록 | 미저장 | 불가 | `displayCategoryCode`만 있음, 카테고리명 변환 미구현 |
| 상품유형(도메인) | **가능(추론)** | 상품명 키워드 파싱 | collected_products.product_type | 가능 | 즙/냉동/생과/가공품 — 상품명에서 자동 추론, 오류 가능성 있음 |
| 무게 (kg) | **가능(추론)** | 상품명 파싱 | collected_products.domain | 가능 | 상품명의 kg/g 단위 추출 |
| kg당 단가 | **가능(파생)** | 계산 | collected_products.domain | 가능 | price / weight_kg |
| 최저가 배지 여부 | **가능(미구현)** | Open API — ordersheet-list-daily | 미저장 | 불가 | `pricingBadge: true/false` — 현재 최저가 상품 여부 파악 가능 |
| 배송 유형 | **가능(미구현)** | Open API — ordersheet-list-daily | 미저장 | 불가 | `shipmentType` (THIRD_PARTY / CGF / CGF LITE) — 로켓배송 여부 구분 가능 |
| 취소율 | **가능(미구현)** | Open API — ordersheet-list-daily | 미저장 | 불가 | `cancelCount / shippingCount`로 주문 취소율 계산 가능 |
| 리뷰 수 | **불가** | — | review_count=0 (고정) | 불가 | 쿠팡 Open API 공식 미지원 — 셀러센터 수동 확인만 가능 |
| 평점 | **불가** | — | review_score=0.0 (고정) | 불가 | 쿠팡 Open API 공식 미지원 — 셀러센터 수동 확인만 가능 |
| 광고 집행 여부 | **가능(수동 업로드)** | Wing 광고 리포트 CSV | 미저장(구현 필요) | 가능(구현 필요) | Open API 공식 미지원 확인. 운영자가 주 1회 Wing에서 리포트 다운로드 → 업로드 |
| 광고비 | **가능(수동 업로드)** | Wing 광고 리포트 CSV | 미저장(구현 필요) | 가능(구현 필요) | 동일 |
| 노출수 | **가능(수동 업로드)** | Wing 광고 리포트 CSV | 미저장(구현 필요) | 가능(구현 필요) | 동일 |
| 클릭수 | **가능(수동 업로드)** | Wing 광고 리포트 CSV | 미저장(구현 필요) | 가능(구현 필요) | 동일 |
| 전환금액 | **가능(수동 업로드)** | Wing 광고 리포트 CSV | 미저장(구현 필요) | 가능(구현 필요) | 동일 |
| CTR/CPC/ROAS | **가능(파생, 수동 업로드 후)** | 계산 | 미저장(구현 필요) | 가능(구현 필요) | 원천 데이터 있을 때만 계산. 분모=0이면 null |

---

## 3. 가능 여부 표기 기준

```
가능:
- 현재 코드/API/DB에서 실제로 확인 가능
- 샘플 응답 또는 저장 데이터가 있음

불가:
- 현재 API 또는 코드에서 제공되지 않음
- 공식 문서/현재 구현 기준으로 수집 불가

확인필요:
- 가능할 수도 있으나 현재 코드에서 확인되지 않음
- 문서 또는 API 응답 추가 확인 필요
```

---

## 4. 쿠팡 광고 데이터 처리 방침

쿠팡 판매자 Open API는 광고 데이터(노출·클릭·전환·광고비)를 공식 제공하지 않는다. (확인 완료)

**확정된 방식:** 운영자가 주 1회 쿠팡 Wing(셀러센터)에서 광고 리포트를 수동 다운로드 → 시스템에 CSV/Excel 업로드

| 구분 | 처리 방침 |
|---|---|
| Open API 자동 수집 | 상품·주문·정산 중심으로 제한 |
| 광고 데이터 | Wing 리포트 수동 업로드 (주 1회) |
| 광고 지표 계산 | 원천 데이터 있을 때만 (분모=0이면 null) |
| 향후 확장 | 공식 광고 API 확인 시 Adapter 패턴으로 연결 |

**Brain 판단 시 주의:** 업로드 주기가 주 1회이므로 광고 데이터는 최대 7일 지연된다.  
Brain 제안에 "X일 전 데이터 기준"을 명시해야 하며, 광고 데이터만으로 즉각 전략 변경을 제안하지 않는다.

**Wing 리포트 컬럼명:** 실제 한글/영문 컬럼명은 샘플 업로드 후 확인 필요.  
컬럼 매핑은 하드코딩하지 않고 설정으로 관리한다.

---

## 5. 현재 코드에서 발견된 주요 이슈

### 4-1. 매출 기준: saleAmount vs settlementAmount

현재 코드는 `saleAmount` (판매액) 기준으로 매출을 집계한다.  
쿠팡 수수료(서비스이용료)가 차감되지 않은 값이다.  
실제 운영자가 받는 금액은 `settlementAmount`이며, API 응답에는 둘 다 있다.

월 단위 실수령액은 `settlement-histories` API의 `finalAmount`로 별도 조회 가능하다.  
(현재 미구현 — KB에 `settlement-histories.md` 있음)

→ Brain 분석 시 "가격 경쟁력"을 판단하려면 정산금액 기준이 더 정확하다.  
→ 현재 Brain에도 "쿠팡 수수료를 고려한 실질 정산금액 관점"이라고 명시되어 있으나, 코드는 불일치.

### 4-2. 광고 데이터 완전 미수집

쿠팡 광고(Wing) API는 현재 연결되지 않았다.  
`coupang.py` 시스템 프롬프트에도 광고 관련 제안 유형이 없다.  
광고 데이터 없이 분석 가능한 범위는 상품 준비도, 가격, 매출 반응에 한정된다.

### 4-3. 재고 데이터 미구현

KB에 `vendor-item-inventory.md`가 있어 API 스펙은 문서화됐지만,  
실제 코드에서는 `stock=0` 고정이다.  
재고 소진 상태에서 광고 제안이 나올 위험이 있다.

### 4-4. 상품유형·무게 추론 오류 가능성

상품명 파싱으로 `product_type`, `weight_kg`을 추론한다.  
상품명이 불규칙하거나 단위 표기가 다르면 오류가 생긴다.  
Brain 판단 시 이 값을 절대 기준으로 쓰지 말고 참고 수준으로만 활용해야 한다.

---

## 5. KB에 없는 API — 추가 필요 여부 검토

| 누락 API | 제공 가능 데이터 | 필요도 | 비고 |
|---|---|---|---|
| **상품 단건 전체 조회** | 이미지 URL, 옵션 목록, 상세설명, 전체 스펙 | 높음 | `product-partial-get`은 배송/반품 정보만. 이미지·옵션 전체는 별도 API 필요 — 존재 여부 확인 필요 |
| **반품/취소 요청 목록 조회** | 취소율, 반품률, 반품 사유 | 중간 | `ordersheet-list-daily`에서 "반품완료건은 이 API 사용"으로 언급됨. KB 없음 |
| **쿠팡 광고 Wing API** | 노출·클릭·전환·광고비 | 높음(장기) | Open API와 완전히 다른 인증 체계. 현재 단계에서는 구현 보류 |

### 우선 확인 권장
`상품 단건 전체 조회` — 이미지와 옵션 정보가 있는지 확인하면 Brain의 "상품 준비도" 판단 범위가 달라진다.  
쿠팡 Open API 공식 문서에 `GET /seller-products/{sellerProductId}` 형태의 단건 전체 조회 API가 있을 가능성이 높다.

---

## 6. Brain이 현재 데이터로 판단 가능한 범위

| 판단 항목 | 현재 가능 여부 | 근거 데이터 |
|---|---|---|
| 상품이 팔리고 있는가 | **가능** | sales_count, sales_revenue (30일) |
| 가격이 적정한가 | **부분 가능** | price, unit_price_per_kg (비교 대상 없음) |
| 시즌에 맞는 상품인가 | **가능** | season_flag, product_type |
| 현재 최저가 상품인가 | **가능(미구현)** | ordersheet-list-daily의 pricingBadge |
| 배송 조건이 적절한가 | **가능(미구현)** | product-partial-get의 deliveryChargeType, deliveryMethod |
| 로켓배송 여부 | **가능(미구현)** | ordersheet-list-daily의 shipmentType |
| 취소율이 높은가 | **가능(미구현)** | ordersheet-list-daily의 cancelCount/shippingCount |
| 재고가 충분한가 | **가능(미구현)** | vendor-item-inventory API 연결 필요 |
| 실수령 정산금액 | **가능(미구현)** | settlement-histories의 finalAmount (월 단위) |
| 상품 이미지 상태 | **불가** | product-list-paged 응답에 이미지 URL 없음 — sample.json 확인 완료 |
| 리뷰/평점이 충분한가 | **불가** | API 미지원 |
| 광고 효율이 어떤가 | **불가(현재)** | Wing API 미연결 |
