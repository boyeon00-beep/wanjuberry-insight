# 상품 조회 (승인불필요) — coupang

> 마지막 검증: 2026-05-18
> 상태: 파일럿

해당 상품의 배송 및 반품지 등 관련 정보를 조회합니다. 본 API의 응답을 활용하여 `상품 수정 (승인불필요)` API(`product-partial-update`)에서 빠르게 정보를 수정 가능. 한국 지역.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products/{sellerProductId}/partial
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| sellerProductId (path) | string | Y | 등록상품 ID. 상품 생성 완료 시 출력된 ID | 30100201234 |

(body 없음)

### 조회 가능 기간
- 최대: N/A (단건 현재값 조회)
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
| message | string | 메시지 | (빈 문자열) |
| data | object | 부분 상품 정보 | (object) |
| data.sellerProductId | number | 등록상품 ID | 30100201234 |
| data.companyContactNumber | string | 반품지 연락처 | 02-123-7678 |
| data.deliveryCharge | number | 기본배송비 | 2500 |
| data.deliveryChargeOnReturn | number | 초도반품배송비 | 0 |
| data.deliveryChargeType | string | 배송비 종류 (`FREE`/`NOT_FREE`/`CHARGE_RECEIVED`/`CONDITIONAL_FREE`) | NOT_FREE |
| data.deliveryCompanyCode | string | 택배사 코드 | HYUNDAI |
| data.deliveryMethod | string | 배송방법 (`SEQUENCIAL`/`COLD_FRESH`/`MAKE_ORDER`/`AGENT_BUY`/`VENDOR_DIRECT`) | SEQUENCIAL |
| data.extraInfoMessage | string | 주문제작 안내 메시지 (배송방법이 주문제작인 경우) | (빈 문자열) |
| data.freeShipOverAmount | number | 무료배송 조건 금액 (100원 이상 단위) | 0 |
| data.outboundShippingPlaceCode | number | 출고지 주소 코드 | 63714 |
| data.pccNeeded | boolean | PCC(개인통관부호) 필수 여부 | false |
| data.remoteAreaDeliverable | string | 도서산간 배송여부 (`Y`/`N`) | N |
| data.returnAddress | string | 반품지 주소 | 서울특별시 송파구 송파대로 570 (신천동) |
| data.returnAddressDetail | string | 반품지 주소 상세 | 타워 |
| data.returnCenterCode | string | 반품지 센터코드 | 56642 |
| data.returnCharge | number | 반품 배송비 (편도) | 2500 |
| data.returnChargeName | string | 반품지명 | 타워730 |
| data.returnZipCode | string | 반품지 우편번호 | 13590 |
| data.unionDeliveryType | string | 묶음 배송 여부 (`UNION_DELIVERY`/`NOT_UNION_DELIVERY`) | NOT_UNION_DELIVERY |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | 상품(XXXXXXXXX)의 데이터가 없습니다 | 존재하는 sellerProductId 확인 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 본 API는 **승인불필요 수정 API와 페어** — 응답을 그대로 수정 body로 활용 가능
- URL API Name: `GET_PARTIAL_PRODUCT_BY_PRODUCT_ID`

## 에이전트 사용 메모
- **수정 전 현재값 확인 자동화 패턴** — 본 API로 조회 → 변경 필드만 교체 → `product-partial-update` 호출
- 응답 필드는 `product-partial-update`의 body 스키마와 동일 → JSON 그대로 수정 후 PUT
- 응답 캐싱 가능 (변경 빈도 낮음). 갱신 시 본 API로 재확인
- 묶음배송 상품 일괄 처리 시: 동일 `outboundShippingPlaceCode` 그룹화에 활용
- 엣지 케이스: 삭제된 상품에 호출 시 400 — 사전에 활성 상품 필터링
- 엣지 케이스: `sellerProductId`는 string 타입의 path지만 응답에서는 number — 타입 변환 주의
