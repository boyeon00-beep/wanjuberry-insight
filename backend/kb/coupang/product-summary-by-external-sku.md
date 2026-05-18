# 상품 요약 정보 조회 (외부 SKU 기준) — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 등록/수정 시 입력한 판매자 상품코드(`externalVendorSku`)로 상품 요약 정보를 조회합니다. 한국, 대만 지역 적용.

**주의:** 상품 등록이 완료된 후 반드시 **1분 이상 경과**한 뒤 호출 (인덱싱 지연 고려).

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products/external-vendor-sku-codes/{externalVendorSkuCode}
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| externalVendorSkuCode (path) | string | Y | 판매자 상품코드 (업체상품코드) | 170816368810 |

(body 없음)

### 조회 가능 기간
- 최대: N/A (단건 조회)
- 기본값: N/A
- **인덱싱 지연:** 등록 직후 1분 이내 조회 시 빈 결과 또는 500 가능 → 1분 이상 대기 후 호출

### 페이지네이션
- 방식: 없음 (동일 SKU에 N개 등록상품이 응답될 수 있음 — 배열 응답)
- 파라미터: -
- 최대 size: -

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | string | 결과 코드 (`SUCCESS`/`ERROR`) | SUCCESS |
| message | string | 결과 메시지 | (빈 문자열) |
| data | array | 업체상품 목록 (조회된 업체상품 개수만큼 반복) | [...] |
| data[].sellerProductId | number | 등록상품 ID | 123 |
| data[].sellerProductName | string | 등록상품명 (20자 이하) | [인xx] 컴퓨터잡지 |
| data[].displayCategoryCode | number | 노출 카테고리 코드 | null |
| data[].categoryId | number | 카테고리 ID (예시 응답에 존재) | 5555 |
| data[].productId | number | Product ID (예시 응답에 존재) | 3333 |
| data[].vendorId | string | 판매자 ID | MASKED |
| data[].mdId | string | MD ID (예시 응답에 존재) | MASKED |
| data[].mdName | string | MD 이름 (예시 응답에 존재) | MASKED |
| data[].saleStartedAt | string | 판매시작일시 (`yyyy-MM-ddTHH:mm:ss`) | 2015-12-28T06:00:00 |
| data[].saleEndedAt | string | 판매종료일시 (`yyyy-MM-ddTHH:mm:ss`. 2099년까지 가능) | 2099-01-01T00:00:00 |
| data[].brand | string | 브랜드 (한글/영어 표준이름) | null |
| data[].statusName | string | 업체상품상태명 (심사중/임시저장/승인대기중/승인완료/부분승인완료/승인반려/상품삭제) | 승인완료 |
| data[].createdAt | string | 판매등록일시 (`yyyy-MM-ddTHH:mm:ss`) | 2015-12-28T18:57:34 |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 500 | API call to HTTP://seller-listing-search.coupang.net:80/vendor/vendor-inventories/scroll(...) failed with status code 500. | 서버 에러. `externalVendorSkuCode` 검증 후 일정 시간 후 재시도 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국, 대만
- **인덱싱 지연:** 등록 후 1분 이내 호출 시 일관성 없는 결과 가능 → 1분 이상 대기
- 동일 `externalVendorSkuCode`로 여러 등록상품 가능 (배열 응답)
- 500 에러는 일시적일 수 있음 → 재시도 권장
- URL API Name: `GET_PRODUCT_BY_EXTERNAL_SKU`

## 에이전트 사용 메모
- **외부 ERP/PIM과 쿠팡 간 SKU 매핑 검증 API** — 외부 시스템의 SKU 코드로 쿠팡 등록 상품 조회
- 등록 직후 호출 패턴: 등록 완료 후 60초 이상 대기 → 본 API로 조회 → `sellerProductId` 수집
- 매핑 결과 캐싱 권장: 같은 SKU 반복 조회 시 외부 시스템에 캐싱 (변경 빈도 낮음)
- 응답이 배열 — 동일 SKU에 복수 상품 존재 시 모두 반환됨. 클라이언트에서 `statusName` 필터로 활성 상품만 추출
- 500 에러 시 지수 백오프(예: 30초, 1분, 2분) 재시도
- 응답 필드 일부(`categoryId`, `productId`, `mdId`, `mdName`)는 스펙 미문서화이나 응답에 포함 → optional 파싱
- season_flag: 신상품 일괄 등록 후 1분 대기 → 본 API로 검증 배치 실행
- 엣지 케이스: 등록 직후 즉시 호출 시 404 또는 빈 배열 가능 — 등록과 조회 사이 sleep 권장
- 엣지 케이스: `displayCategoryCode`가 null인 케이스 존재 → null 가드
