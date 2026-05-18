# 상품 아이템별 수량 변경 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 아이템별 재고수량을 변경합니다. 판매요청 신청 후 승인완료되어 옵션ID(`vendorItemId`)가 발급된 경우 사용 가능. 한국 지역.

## Endpoint
- Method: PUT
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/quantities/{quantity}
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorItemId (path) | number | Y | 옵션 ID. 벤더아이템 고유 번호 | 3572784698 |
| quantity (path) | number | Y | 변경할 재고 수량 | 100 |

(본 API는 body/query 미사용 — `not require body`)

### 조회 가능 기간
- 최대: N/A
- 기본값: N/A

### 페이지네이션
- 방식: 없음
- 파라미터: -
- 최대 size: -

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | string | 결과 코드 (`SUCCESS`/`ERROR`) | SUCCESS |
| message | string | 결과 메시지 | 재고 변경을 완료했습니다. |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 유효하지 않은 재고수량입니다. | 올바른 quantity 값 확인 |
| 400 | 재고변경에 실패했습니다. [옵션ID[...] : 삭제된 상품은 변경이 불가능합니다.] | 삭제 여부 확인 |
| 400 | 재고변경에 실패했습니다. [vendoritemid ... not found] | `vendorItemId` 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 옵션 ID(`vendorItemId`)가 발급된 상품만 사용 가능
- 삭제된 상품은 수량 변경 불가
- URL API Name: `UPDATE_PRODUCT_QUANTITY_BY_ITEM`

## 에이전트 사용 메모
- **재고 동기화 에이전트 핵심 API** — 외부 WMS/ERP의 재고 수량을 본 API로 쿠팡에 반영
- 자동화 패턴: 재고 변경 이벤트 발생 → vendorItemId 매핑 → 본 API 호출 → 응답 검증
- 응답 본문은 단순 (`code`/`message`만) — `data` 없음
- 변경 후 vendor-item-status 조회로 적용 확인 권장 (대규모 배치 시)
- 0으로 설정 시 사실상 품절 처리 (판매 중지와는 별개 — 판매 중지는 별도 API 사용)
- season_flag: 시즌 종료 후 재고 0 처리, 시즌 시작 시 재고 충전 — 배치 호출
- 엣지 케이스: 음수 quantity 입력 시 400 — 클라이언트에서 max(0, qty) 처리
- 엣지 케이스: 삭제된 옵션 ID에 호출 시 400 — 사전에 활성 옵션만 필터링
