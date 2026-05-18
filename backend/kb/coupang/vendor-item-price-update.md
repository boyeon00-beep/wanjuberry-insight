# 상품 아이템별 가격 변경 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

상품 아이템별 판매가격을 변경합니다. 판매요청 신청 후 승인완료되어 옵션ID(`vendorItemId`)가 발급된 경우 사용 가능. `forceSalePriceUpdate=true`로 요청 시 변경 비율 제한 없이 가격변경 가능. 한국 지역.

## Endpoint
- Method: PUT
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/prices/{price}
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body

#### Path Segment
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorItemId | number | Y | 옵션 ID. 벤더아이템에 부여되는 고유 번호 | 3572784698 |
| price | number | Y | 변경할 가격. **최소 10원 단위** (1원 단위 불가) | 49000 |

#### Query String
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| forceSalePriceUpdate | boolean | N | 가격 변경 비율 제한 여부. `false`(기본, 비율 제한 적용) / `true`(제한 없음). 입력 실수 방지용으로 기본 비율 제한이 적용되며, `true` 추가 시 제한 해제 | true |

### 조회 가능 기간
- 최대: N/A (변경 API)
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
| message | string | 결과 메시지 | 가격 변경을 완료했습니다. |
| data | object | 데이터 (본 API에서는 null) | null |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 가격변경에 실패했습니다. [옵션ID[...] : 판매가 변경이 불가능합니다. 변경 전 판매가의 최대 50% 인하/최대 100% 인상까지 변경가능합니다.] | 가격 변경 범위(-50%~+100%) 내 값 사용 또는 `forceSalePriceUpdate=true` |
| 400 | 자동생성옵션의 가격을 직접 수정할 수 없습니다. 기준 판매자옵션 가격으로 자동생성옵션 가격도 변경할 수 있습니다. | 기준 판매자옵션 가격 조정 → 자동생성옵션은 수량 배수만큼 자동 반영. 이미 자동생성옵션 가격을 직접 수정한 경우는 WING에서만 변경 가능 |
| 400 | 가격변경에 실패했습니다. [옵션ID[...] : 삭제된 상품은 변경이 불가능합니다.] | `vendorItemId`가 삭제되었는지 확인 |
| 400 | 가격변경에 실패했습니다. [옵션ID[...]: 가격은 최소 10원 단위로 입력가능합니다. (1원단위 입력 불가)] | 최소 10원 단위로 입력 |
| 400 | 유효하지 않은 ID입니다. | `vendorItemId` 값 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 옵션 ID(`vendorItemId`)가 발급된 상품(판매요청 신청 후 승인완료)만 사용 가능
- 가격은 **최소 10원 단위** (1원 단위 입력 불가)
- 기본 가격 변경 범위: **-50% ~ +100%** (변경 전 판매가 기준). 초과 시 `forceSalePriceUpdate=true` 사용
- 자동생성옵션은 직접 가격 수정 불가 → 기준 판매자옵션 변경 또는 WING 사용
- 삭제된 상품은 가격 변경 불가
- URL API Name: `UPDATE_PRODUCT_PRICE_BY_ITEM`

## 에이전트 사용 메모
- **가격 자동화 에이전트 핵심 API** — 경쟁사 가격 추적 → 자동 조정 워크플로우
- 가격 변경 비율 가드: 무인 자동화에서는 `forceSalePriceUpdate=false` 유지 권장 (입력 실수/스크립트 오류 방어막)
- 큰 폭 가격 인상/인하가 필요한 프로모션 종료 시: `forceSalePriceUpdate=true`로 일괄 처리
- 10원 단위 라운딩: 클라이언트에서 사전 라운딩 (예: 49001 → 49000)
- 자동생성옵션 가격 변경 실패 시 → 기준 옵션 변경으로 우회 또는 WING 수동 작업 큐로 이동
- 응답 `code="ERROR"` 시 `message`에 옵션ID와 사유 포함 → 로그/알림에 그대로 사용 가능
- season_flag: 시즌 종료/시작 시 대량 가격 변경 직전, vendor-item-status 조회로 활성 옵션만 추출 후 적용
- 엣지 케이스: HMAC 서명 시 URL 인코딩 일관성 — path의 `{price}`가 숫자 그대로 들어가는지 확인
- 엣지 케이스: 응답 `data`가 항상 null — 응답 본문으로 신규 가격 확인 불가. 변경 후 vendor-item-status API로 재확인 권장
