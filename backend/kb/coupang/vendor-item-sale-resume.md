# 상품 아이템별 판매 재개 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 아이템별 판매상태를 판매중으로 변경합니다. 옵션ID(`vendorItemId`)가 발급된 상품만 사용 가능. 한국 지역.

## Endpoint
- Method: PUT
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/sales/resume
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
| message | string | 결과 메시지 | 판매가 재개되었습니다. |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 판매재개에 실패했습니다. [옵션ID[...] : 삭제된 상품은 변경이 불가능합니다.] | 삭제 여부 확인 |
| 400 | 판매재개에 실패했습니다. [옵션ID(...)은 쿠팡의 모니터링에 의해 '판매중지'된 상품입니다. | 쿠팡 판매자콜센터/온라인 문의 |
| 400 | 판매재개에 실패했습니다. [vendoritemid *** not found] | `vendorItemId` 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 옵션 ID(`vendorItemId`)가 발급된 상품만 사용 가능
- **쿠팡 모니터링에 의해 판매중지된 상품은 본 API로 재개 불가** → 판매자콜센터/온라인 문의 필요
- 삭제된 상품은 재개 불가
- URL API Name: `RESUME_PRODUCT_SALES_BY_ITEM`

## 에이전트 사용 메모
- **품절 해소 후 자동 재판매 워크플로우 핵심 API**
- 호출 순서 예: 재고 충전(`vendor-item-quantity-update`) → 판매 재개(본 API) → 상태 확인(`vendor-item-inventory`)
- 응답 본문 단순 (`code`/`message`만) — `data` 없음
- 쿠팡 모니터링 차단 상품은 본 API로 재개 불가 → 실패 응답을 큐로 적재 후 수동 처리 라우팅
- season_flag: 시즌 시작 시 휴면 상품 일괄 재개
- 엣지 케이스: 모니터링 차단 상품에 호출 시 명시 메시지로 응답 → 패턴 매칭으로 자동 분류
- 엣지 케이스: 이미 판매중인 옵션에 재호출은 success 응답 (idempotent 추정)
