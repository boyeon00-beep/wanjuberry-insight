# 상품 목록 페이징 조회 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

등록상품 목록을 페이징 조회합니다. 한국, 대만 지역 적용.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorId | string | Y | 판매자 ID. 쿠팡에서 발급한 고유 코드 | MASKED |
| nextToken | number | N | 다음 페이지 키값. 첫 페이지는 생략 또는 1 입력 | 2 |
| maxPerPage | number | N | 페이지당 건수. 기본 10, 최대 100 | 100 |
| sellerProductId | number | N | 등록상품 ID | 239092172 |
| sellerProductName | string | N | 등록상품명 검색. **20자 이하** | 헬로키티 |
| status | string | N | 업체상품상태 (`IN_REVIEW`/`SAVED`/`APPROVING`/`APPROVED`/`PARTIAL_APPROVED`/`DENIED`/`DELETED`) | APPROVED |
| manufacture | string | N | 제조사 | (string) |
| createdAt | string | N | 상품등록일시 `yyyy-MM-dd` 형식. 해당일 00:00:00~23:59:59 범위 조회 | 2015-12-17 |
| violationTypes | array(string) | N | 위반 유형 검색 필드. 다중 지정 가능 (`NO_VA_V2`: 상품정보 검증 필요-노출제한, `MOTA_V2`: 누락된 필수 구매옵션-노출제한, `ATTR`: 옵션 수정 필요-노출 낮음) | ATTR, MOTA_V2 |
| violationTypeAndOr | string | 조건부 | `violationTypes`가 2개 이상일 때 필수. `AND` / `OR` | OR |

### 조회 가능 기간
- 최대: N/A (특정 일자 조회는 `createdAt` 1일 단위)
- 기본값: 없음

### 페이지네이션
- 방식: cursor (nextToken)
- 파라미터: `nextToken` + `maxPerPage`
- 최대 size: 100
- 다음 페이지 없으면 응답 `nextToken`이 빈 문자열

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | string | 결과 코드 (`SUCCESS`/`ERROR`. 문서에는 Number로 표기되어 있으나 예시는 String) | SUCCESS |
| message | string | 결과 메시지 | (빈 문자열) |
| nextToken | string | 다음 페이지. 없으면 빈 문자열 | 2 |
| data | array | 등록상품 목록 | [...] |
| data[].sellerProductId | number | 등록상품 ID (문서엔 String, 예시는 Number) | 239092172 |
| data[].sellerProductName | string | 등록상품명 | R07 헬로키티 미니낚시놀이 |
| data[].displayCategoryCode | number | 노출 카테고리 코드 | 77413 |
| data[].categoryId | number | 카테고리 ID | 2102 |
| data[].productId | number | Product ID | 14784194 |
| data[].vendorId | string | 판매자 ID | MASKED |
| data[].mdId | string | MD ID (예시에 존재, 스펙 미문서화) | MASKED |
| data[].mdName | string | MD 이름 (예시에 존재, null 가능) | null |
| data[].saleStartedAt | string | 판매시작일시 (`yyyy-MM-ddTHH:mm:ss`) | 2017-02-14T06:00:00 |
| data[].saleEndedAt | string | 판매종료일시 (`yyyy-MM-ddTHH:mm:ss`) | 2099-12-31T00:00:00 |
| data[].brand | string | 브랜드 | 상세설명별도참조 |
| data[].statusName | string | 등록상품 상태 한글명 (심사중/임시저장/승인대기중/승인완료/부분승인완료/승인반려/상품삭제) | 승인완료 |
| data[].createdAt | string | 판매등록일시 (`yyyy-MM-ddTHH:mm:ss`) | 2017-02-13T02:09:47 |

### 상태 코드
| 코드 | 의미 |
|---|---|
| 200 | OK |
| 400 | 요청변수확인 — `업체코드는 반드시 입력되어야 합니다.`, `Format of createdAt is yyyy-MM-dd` |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국, 대만
- `vendorId` 필수
- `sellerProductName` 검색은 **20자 이하**
- `createdAt`은 **`yyyy-MM-dd`** 형식 (`yyyy-MM-ddTHH:mm:ss` 아님)
- 페이지당 최대 100건
- `violationTypes` 2개 이상 시 `violationTypeAndOr` 필수
- 응답 `code` 필드 타입 표기와 실제값 차이 주의 (문서 Number / 실제 String)
- URL API Name: `GET_PRODUCTS_BY_QUERY`

## 에이전트 사용 메모
- **상품 카탈로그 동기화 에이전트 핵심 API** — 전체 상품 목록 페이징으로 수집 후 로컬 DB 동기화
- 페이지네이션: 첫 호출은 `nextToken` 생략, 응답 `nextToken`이 빈 문자열이면 종료
- 상태별 필터링: 운영상 `DELETED` 제외하고 수집, `APPROVED`/`PARTIAL_APPROVED`만 노출 처리
- 노출 문제 진단: `violationTypes=ATTR,MOTA_V2,NO_VA_V2` + `violationTypeAndOr=OR`로 노출 제한/낮음 상품 일괄 조회
- `mdId`/`mdName`은 문서엔 없지만 응답에 포함 — 파싱 시 optional 처리
- `code` 타입은 String("SUCCESS"/"ERROR")로 비교 권장 (다른 API의 200 number와 다름)
- 엣지 케이스: `createdAt=yyyy-MM-dd` 형식 외 입력 시 400 오류
- 엣지 케이스: `sellerProductName` 21자 이상 검색 시 거부 가능성 → 클라이언트에서 사전 자르기
