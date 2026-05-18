# 상품 수정 (승인불필요) — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

배송 및 반품지 관련 정보를 별도의 승인 절차 없이 빠르게 수정합니다. **'임시저장중', '승인대기중'인 상품은 수정 불가**. 한국 지역.

## Endpoint
- Method: PUT
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products/{sellerProductId}/partial
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |
| Content-Type | Y | application/json |

### Query Parameters / Body

#### Path Segment
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| sellerProductId | string | Y | 등록상품 ID. 상품 생성 완료 시 출력된 ID | 30100208559 |

#### Body (sellerProductId 외 모두 비필수, 원하는 항목만 입력하여 수정)
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| sellerProductId | number | Y | 등록상품 ID (path와 동일해야 함) | 30100201234 |
| companyContactNumber | string | N | 반품지 연락처. Wing 또는 반품지 생성 API로 등록 후 확인 | 02-123-1234 |
| deliveryCharge | number | N | 기본배송비. 유료/조건부 무료 시 편도 금액 | 2500 |
| deliveryChargeOnReturn | number | N | 초도반품배송비. 무료배송 시 반품 시 소비자 지불 | 0 |
| deliveryChargeType | string | N | 배송비 종류. `FREE`/`NOT_FREE`/`CHARGE_RECEIVED`/`CONDITIONAL_FREE` | CONDITIONAL_FREE |
| deliveryCompanyCode | string | N | 택배사 코드 (택배사 코드표 참조) | HYUNDAI |
| deliveryMethod | string | N | 배송방법. `SEQUENCIAL`(일반/순차)/`COLD_FRESH`(신선냉동)/`MAKE_ORDER`(주문제작)/`AGENT_BUY`(구매대행)/`VENDOR_DIRECT`(설치배송/판매자 직접 전달; INSTRUCTURE·MAKE_ORDER_DIRECT는 VENDOR_DIRECT로 통합) | SEQUENCIAL |
| extraInfoMessage | string | N | 주문제작 안내 메시지 (배송 방법이 주문제작인 경우) | (string) |
| freeShipOverAmount | number | N | 무료배송 조건 금액. CONDITIONAL_FREE 사용 시 (100원 이상 단위), 무료배송이면 0 | 10000 |
| outboundShippingPlaceCode | number | N | 출고지 주소 코드. 묶음배송 선택 시 필수 (출고지 조회 API로 조회) | 63714 |
| outboundShippingTimeDay | number | N | 기준 출고일(일). 주문일(D-Day) 이후 출고 예정 일자. 당일출고 / 다음날(D+1) 출고 모두 `1` 입력 | 2 |
| sameDayShipping | object | N | 당일배송 설정 | (object) |
| sameDayShipping.active | boolean | N | 당일배송 설정 가능여부 | true |
| sameDayShipping.cutOffTimeHour | number | N | 당일출고 마감 시(시). 범위 10~23 | 18 |
| sameDayShipping.cutOffTimeMinute | number | N | 마감 시간(분). `active=true`인 경우 0이어야 함 | 0 |
| sameDayShipping.cutOffTimeZone | string | N | 시스템 관리. `active=true`면 기본값 `KR` | KR |
| pccNeeded | boolean | N | PCC(개인통관부호) 필수 여부. 해외구매대행 상품의 경우 사용. 기본 false (`true`: PCC 입력 후 구매 가능 — 발주서에 포함 / `false`: PCC 없이 구매 가능) | false |
| remoteAreaDeliverable | string | N | 도서산간 배송여부. `Y`/`N` | N |
| returnAddress | string | N | 반품지 주소 | 서울특별시 송파구 송파대로 12길 |
| returnAddressDetail | string | N | 반품지 주소 상세 | 123호 |
| returnCenterCode | string | N | 반품지 센터코드. Wing 또는 반품지 생성 API로 추출. 반품지 생성 불가 시 `NO_RETURN_CENTERCODE` 입력 가능 (단, 반품자동연동 굿스플로우는 계약 택배사 필수, 센터코드 입력 필수) | 1000274592 |
| returnCharge | number | N | 반품 배송비 (반품회수 시 편도) | 2500 |
| returnChargeName | string | N | 반품지명 | 반품지명_1 |
| returnZipCode | string | N | 반품지 우편번호 | 15200 |
| unionDeliveryType | string | N | 묶음 배송 여부. `UNION_DELIVERY`(가능) / `NOT_UNION_DELIVERY`(불가). 묶음 조건: 출고지 정보 필수 + 같은 출고지만 묶음 + 착불배송 불가 설정 불가 | UNION_DELIVERY |

### 조회 가능 기간
- 최대: N/A (수정 API)
- 기본값: N/A

### 페이지네이션
- 방식: 없음
- 파라미터: -
- 최대 size: -

## Response

### 주요 필드
응답은 외부 HTTP 래퍼 + 내부 API 결과 이중 구조.

| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | string | 외부 HTTP 상태 코드 (문자열) | "200" |
| message | string | 외부 메시지 | (빈 문자열) |
| data | object | 내부 응답 본문 | (object) |
| data.code | string | 결과 코드 (`SUCCESS`/`ERROR`) | SUCCESS |
| data.message | string | 메시지 | (빈 문자열) |
| data.data | number | 수정된 등록상품 ID (= 입력한 sellerProductId) | 30100201234 |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 업체상품아이디를 다시 확인해주세요. | path의 sellerProductId와 body의 sellerProductId 일치 확인 |
| 400 | 업체상품아이디를 반드시 입력해주세요. | body에 sellerProductId 포함 |
| 400 | 존재하지 않는 등록상품아이디 [xxxxxx]입니다. | sellerProductId 존재 여부 확인 |
| 400 | 삭제된 상품은 변경이 불가능합니다. | 삭제된 상품 아닌지 확인 |
| 400 | 승인 대기중 상품은 수정할 수 없습니다. | 상태 확인 |
| 400 | 생성이 진행중인 상품은 수정할 수 없습니다. | '임시저장중' 아닌지 확인 |
| 500 | 상품 수정이 실패했습니다. 쿠팡관리자에게 문의해주세요 | 시스템 에러 — 쿠팡 문의 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- **'임시저장중', '승인대기중' 상품 수정 불가** (`삭제됨`도 불가)
- path와 body의 `sellerProductId`가 일치해야 함
- 수정 가능 속성은 **배송/반품지 관련**으로 한정 — 다른 속성은 별도 API(승인필요) 사용
- `deliveryChargeType` 조합 규칙:
  - `FREE` 설정 시 → `deliveryChargeOnReturn` + `returnCharge` 금액 설정
  - `NOT_FREE` 설정 시 → `deliveryCharge` + `returnCharge` 금액 설정
  - `CONDITIONAL_FREE` 설정 시 → `deliveryCharge` + `returnCharge` + `freeShipOverAmount`
  - `CHARGE_RECEIVED` 설정 시 → 착불배송 가능 카테고리만 (콜센터 공유)
- `freeShipOverAmount`는 100원 이상 단위, 무료배송이면 0
- `outboundShippingTimeDay`: 당일/다음날(D+1) 모두 `1` (`0`이 아닌 점 주의)
- `sameDayShipping.cutOffTimeHour`는 10~23 사이만 허용
- `sameDayShipping.active=true`일 때 `cutOffTimeMinute`는 0
- 묶음 배송: 출고지 같은 상품만 가능 / 착불배송 불가 설정 불가
- 반품지 정보는 Wing/반품지 생성 API 선행 등록 필요 (또는 `NO_RETURN_CENTERCODE` 사용)
- URL API Name: `UPDATE_PARTIAL_PRODUCT`

## 에이전트 사용 메모
- **빠른 배송/반품 정보 일괄 수정 자동화** — 승인 대기 없이 즉시 반영
- 적용 전 체크: 대상 상품의 `statusName`이 `APPROVED`/`PARTIAL_APPROVED`인지 확인 (그 외는 400 오류)
- 부분 수정 활용: 변경하려는 필드만 body에 포함 (다른 필드는 기존값 유지)
- 응답 파싱 시 외부 `code="200"`과 내부 `data.code="SUCCESS"` 모두 확인
- 묶음배송 활성화 시: 동일 `outboundShippingPlaceCode`인 상품들끼리 묶이도록 사전 정렬
- 시즌 변경 시 일괄: 배송비 정책/반품지 변경을 본 API로 배치 적용
- 엣지 케이스: path와 body의 `sellerProductId` 불일치 → 400. 자동화 시 항상 함께 세팅
- 엣지 케이스: 응답 `data.code="ERROR"`이면 message에 상세 사유 — 외부 200이라도 실패 가능
- 엣지 케이스: `sameDayShipping.cutOffTimeHour` 외 범위 입력 시 400
- 엣지 케이스: `pccNeeded=true` 설정 시 발주서에 PCC 포함 → 해외구매대행 데이터 처리 파이프라인에 추가
