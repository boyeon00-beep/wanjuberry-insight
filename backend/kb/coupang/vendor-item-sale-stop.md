# 상품 아이템별 판매 중지 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 아이템별 판매상태를 판매중지로 변경합니다. 옵션ID(`vendorItemId`)가 발급된 상품만 사용 가능. 한국 지역.

## Endpoint
- Method: PUT
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/sales/stop
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

(body 없음)

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
| message | string | 결과 메시지 | 판매 중지 처리되었습니다. |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 판매중지에 실패했습니다. [옵션ID[...] : 삭제된 상품은 변경이 불가능합니다.] | 삭제 여부 확인 |
| 400 | 판매중지에 실패했습니다. [vendoritemid *** not found] | `vendorItemId` 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 옵션 ID(`vendorItemId`)가 발급된 상품만 사용 가능
- 삭제된 상품은 중지 불가
- URL API Name: `STOP_PRODUCT_SALES_BY_ITEM`

## 에이전트 사용 메모
- **재고 소진/리콜/문제 발견 시 즉시 판매 중지 자동화 API**
- 호출 후 `vendor-item-inventory`로 `onSale=false` 확인 권장
- 자동화 패턴: 재고 0 임박 + 입고 일정 없음 → 사전 중지, 또는 품질 이슈 알림 수신 → 즉시 중지
- 응답 본문 단순 (`code`/`message`만)
- `vendor-item-sale-resume`로 다시 활성화 가능 (쿠팡 모니터링 차단 아닌 경우)
- season_flag: 시즌 종료 시 비활성 옵션 일괄 중지
- 엣지 케이스: 이미 중지된 옵션에 재호출은 success 응답 (idempotent 추정)
- 엣지 케이스: 판매 중지 = 노출 중지, 재고가 남아도 판매 불가
