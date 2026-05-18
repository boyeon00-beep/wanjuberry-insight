# 상품 등록 현황 조회 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

판매자가 등록할 수 있는 상품수와 현재 등록되어 있는 상품수를 조회합니다. 생성 가능한 최대 상품수(`permittedCount`)가 `null`일 경우 제한없이 상품등록이 가능합니다. 한국 지역 한정 API.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products/inflow-status
- 인증: HMAC Signature (Authorization 헤더)

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |
| Content-Type | N | application/json |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| (없음) | - | - | 본 API는 path/query/body 파라미터 없음 (`not require body`) | - |

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
| code | string | 결과 코드 (`SUCCESS` / `ERROR`) | SUCCESS |
| message | string | 결과 메시지 | (빈 문자열) |
| data | object | 데이터 | (object) |
| data.vendorId | string | 판매자 ID | MASKED |
| data.restricted | boolean | 상품 생성 불가 여부 (`false`: 생성가능, `true`: 생성불가능) | false |
| data.registeredCount | number | 등록된 상품수 (삭제 상품 제외) | 8125 |
| data.permittedCount | number | 생성 가능한 최대 상품수. `null`이면 제한 없음 | 10000 |

### 상태 코드
| 코드 | 의미 |
|---|---|
| 200 | OK |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- `permittedCount`가 `null`이면 등록 제한 없음
- 본 API는 단순 현황 조회 — 등록/수정/삭제 시 별도 API 사용
- URL API Name: `GET_INFLOW_STATUS`

## 에이전트 사용 메모
- **신규 상품 등록 자동화의 사전 체크 API** — 등록 직전에 본 API로 잔여 슬롯 확인
- 잔여 가능 수량 = `permittedCount - registeredCount` (단, `permittedCount`가 null이면 무제한)
- `restricted=true`인 경우 신규 등록 시도 금지 → 별도 알림/큐 대기
- 캐싱 권장: 잦은 호출 대신 일 1회 또는 신규 등록 배치 직전에만 조회
- season_flag: 시즌 신상 대량 등록 직전에 본 API로 사전 검증
- 엣지 케이스: `code`가 문자열(`SUCCESS`/`ERROR`)임을 주의 — 다른 API의 number 코드와 다름
