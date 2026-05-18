# 상품 아이템별 수량/가격/상태 조회 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 아이템별 재고수량, 판매가격, 판매상태를 조회합니다. 한국 지역.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/inventories
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorItemId (path) | number | Y | 옵션 ID. 벤더아이템 고유 번호 | 3000000000 |

(본 API는 body 없음)

### 조회 가능 기간
- 최대: N/A (현재 상태 조회)
- 기본값: N/A

### 페이지네이션
- 방식: 없음
- 파라미터: -
- 최대 size: -

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | string | 결과 코드 (`SUCCESS`/`ERROR`. 문서엔 Number지만 예시는 String) | SUCCESS |
| message | string | 결과 메시지 | (빈 문자열) |
| data | object | 조회된 옵션 수량/가격/상태 | (object) |
| data.sellerItemId | number | 옵션 아이디 | 3000000000 |
| data.amountInStock | number | 옵션 잔여 수량 | 0 |
| data.salePrice | number | 옵션 판매 가격 | 32000 |
| data.onSale | boolean | 옵션 판매 상태 (`true`/`false`) | true |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 유효한 옵션이 없습니다: [vendorItemId=...] | `vendorItemId` 값/삭제 여부 확인 |
| 400 | 유효하지 않은 ID가 입력되었습니다. | `vendorItemId` 형식 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 옵션 ID(`vendorItemId`)가 발급된 상품만 사용 가능
- 응답 `code`는 String("SUCCESS"/"ERROR")로 비교 (문서 Number 표기와 실제 String 차이)
- URL API Name: `GET_PRODUCT_QUANTITY_PRICE_STATUS`

## 에이전트 사용 메모
- **재고/가격/판매 상태 단건 조회의 표준 API** — 변경 직후 검증 또는 외부 시스템 동기화 시 사용
- `vendor-item-price-update`/`vendor-item-quantity-update` 호출 후 본 API로 변경 반영 확인
- `onSale=false`이면 판매 중지 상태 → `vendor-item-sale-resume`로 재개 또는 `vendor-item-sale-stop`로 유지
- `amountInStock=0` + `onSale=true`이면 사실상 품절 표시 (재고 0이지만 판매 중지 아님)
- 대량 조회 필요 시 본 API를 N회 호출 (단건 조회만 지원) → 클라이언트에서 동시 호출 제한 권장
- 응답 필드명: 응답의 `sellerItemId`는 요청 path의 `vendorItemId`와 동일한 의미 (이름 다름 — 주의)
- 엣지 케이스: 응답의 `sellerItemId`가 `vendorItemId`라는 점 — 매핑 코드에서 혼동 주의
- 엣지 케이스: 삭제된 옵션 ID는 400 — 사전 필터 또는 try/except로 graceful 처리
