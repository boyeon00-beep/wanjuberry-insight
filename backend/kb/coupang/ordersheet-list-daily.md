# 발주서 목록 조회 (일단위 페이징) — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

발주서 목록을 하루단위 페이징 형태로 조회합니다. 예: `2020-02-01 ~ 2020-02-03`. 페이지당 row 사이즈는 `maxPerPage`로 조정, 다음 페이지는 `nextToken`으로 획득합니다. Path Parameter 일부 제외, 발주서 목록 조회(분단위 전체)와 전반적으로 구성이 같습니다. 한국/대만 지역만 적용 가능.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/openapi/apis/api/v5/vendors/{vendorId}/ordersheets
- 인증: HMAC Signature (Authorization 헤더, `hmac-signature` 가이드 참조)

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature (hmac-signature 가이드 참조) |
| Content-Type | N | application/json |

### Query Parameters / Body

#### Path Segment
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorId | string | Y | 판매자 ID. 쿠팡에서 업체에 발급한 고유 코드 | A00012345 (MASKED 권장) |

#### Query String
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| createdAtFrom | string | Y | 검색 시작일시(ISO-8601). `yyyy-mm-dd%2B09:00` 형태 (`+09:00`을 `%2B09:00`로 URL 인코딩) | 2025-07-01%2B09:00 |
| createdAtTo | string | Y | 검색 종료일시(ISO-8601). 최대 31일까지 조회 가능 | 2025-07-31%2B09:00 |
| status | string | Y | 발주서 상태. `ACCEPT`(결제완료) / `INSTRUCT`(상품준비중) / `DEPARTURE`(배송지시) / `DELIVERING`(배송중) / `FINAL_DELIVERY`(배송완료) / `NONE_TRACKING`(업체 직접 배송, 추적불가) | INSTRUCT |
| nextToken | string | N | 다음 페이지 조회용 토큰. 첫 페이지 호출 시 불필요 | 448537989 |
| maxPerPage | number | N | 페이지당 최대 조회 요청 값. default 50 | 50 |
| searchType | string | N | `timeFrame`이면 발주서 목록 조회(분단위 전체)로 수행, 그 외에는 본 API(일단위 페이징)로 수행 | (생략) |

### 조회 가능 기간
- 최대: **31일** (`createdAtFrom` ~ `createdAtTo`)
- 기본값: 없음 (필수 입력)

### 페이지네이션
- 방식: cursor (token 기반)
- 파라미터: `nextToken`(다음 페이지) + `maxPerPage`(페이지 크기)
- 최대 size: 50
- 마지막 페이지인 경우 응답 `nextToken`이 빈 문자열로 반환

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | number | 서버 응답 코드 | 200 |
| message | string | 서버 응답 메시지 | OK |
| data | array | 결과 리스트. 결과 없을 시 빈 리스트 | [...] |
| data[].shipmentBoxId | number | 배송번호(묶음배송번호) | 64253897***6401429 |
| data[].orderId | number | 주문번호 | 22000009546234 |
| data[].orderedAt | string | 주문일시(ISO-8601) `YYYY-MM-DDThh:mm:ss.ssssss±hh:mm` | 2025-01-15T14:17:13.973885-08:00 |
| data[].orderer | object | 주문자 정보 | (object) |
| data[].orderer.name | string | 주문자 이름 | 신*희 |
| data[].orderer.email | string | 주문자 email (미사용, 빈값) | (빈 문자열) |
| data[].orderer.safeNumber | string | 수취인 연락처(안심번호) (E.164) | +1(555)444-1234 |
| data[].orderer.ordererNumber | string | 주문자 연락처(실전화번호) (E.164). null 가능 | null |
| data[].paidAt | string | 결제일시(ISO-8601) | 2025-01-15T14:17:13.973885-08:00 |
| data[].status | string | 발주서 상태 (ACCEPT/INSTRUCT/DEPARTURE/DELIVERING/FINAL_DELIVERY/NONE_TRACKING) | FINAL_DELIVERY |
| data[].shippingPrice | object | 배송비 (Money 타입) | {currencyCode, units, nanos} |
| data[].shippingPrice.currencyCode | string | 통화 코드 (ISO-4217, 대문자 3자) | KRW |
| data[].shippingPrice.units | number | 통화 정수 부분 (64bit) | 5000 |
| data[].shippingPrice.nanos | number | 통화 소수점 부분 (32bit, [-9999999999, 999999999]) | 0 |
| data[].remotePrice | object | 도서산간배송비 (Money 타입; null 가능) | null |
| data[].remoteArea | boolean | 도서산간여부 | false |
| data[].parcelPrintMessage | string | 배송메시지 (optional) | 문 앞 |
| data[].splitShipping | boolean | 분리배송 여부 | false |
| data[].ableSplitShipping | boolean | 분리배송 가능 여부 | false |
| data[].receiver | object | 수취인 정보 | (object) |
| data[].receiver.name | string | 수취인 이름 | 신*희 |
| data[].receiver.safeNumber | string | 수취인 안심번호 (E.164) | +1(555)444-1234 |
| data[].receiver.receiverNumber | string | 수취인 실전화번호 (E.164; null 가능) | null |
| data[].receiver.addr1 | string | 수취인 배송지1 | 경기 오산시 가수동 **아파트 |
| data[].receiver.addr2 | string | 수취인 배송지2 | 109동 *호 |
| data[].receiver.postCode | string | 수취인 우편번호 | 447-700 |
| data[].orderItems | array | 배송 대상 아이템 목록 | (array) |
| data[].orderItems[].vendorItemPackageId | number | vendorItemPackageId (미사용, 없으면 0) | 0 |
| data[].orderItems[].vendorItemPackageName | string | vendorItemPackageName (미사용) | (string) |
| data[].orderItems[].productId | number | productId (optional, 없으면 0) | 31846051 |
| data[].orderItems[].vendorItemId | number | 옵션 ID | 3242596358 |
| data[].orderItems[].vendorItemName | string | 노출상품명 | 인디고뱅크키즈 ..., 160호 |
| data[].orderItems[].shippingCount | number | 구매 수량 (발주가능 수량 = shippingCount - (holdCountForCancel + cancelCount)) | 1 |
| data[].orderItems[].salesPrice | object | 개당 상품 가격 (Money) | (Money) |
| data[].orderItems[].orderPrice | object | 결제 가격 (= salesPrice × shippingCount) | (Money) |
| data[].orderItems[].discountPrice | object | 총 할인 가격 (= instantCouponDiscount + downloadableCouponDiscount + coupangDiscount) | (Money) |
| data[].orderItems[].instantCouponDiscount | object | 즉시할인 쿠폰 할인 금액 | (Money) |
| data[].orderItems[].downloadableCouponDiscount | object | 다운로드 쿠폰 할인 금액 | (Money) |
| data[].orderItems[].coupangDiscount | object | 쿠팡 지원 할인 (장바구니/카테고리 쿠폰 등) | (Money) |
| data[].orderItems[].externalVendorSkuCode | string | external code (optional) | 170816368810 |
| data[].orderItems[].etcInfoHeader | string | 상품별 개별 입력 항목 (optional) | null |
| data[].orderItems[].etcInfoValue | string | 상품별 개별 입력값 (optional; 값 없음 — etcInfoValues 사용 권장) | null |
| data[].orderItems[].etcInfoValues | array | 상품별 개별 입력값 리스트 (optional) | ["추가메시지1", "추가메시지2"] |
| data[].orderItems[].sellerProductId | number | 등록상품 ID | 80240831 |
| data[].orderItems[].sellerProductName | string | 등록상품명 | 인디고뱅크키즈 A5 ... |
| data[].orderItems[].sellerProductItemName | string | 등록옵션명 | 07 DARK GREY 160호 |
| data[].orderItems[].firstSellerProductItemName | string | 최초등록옵션명 | 07 DARK GREY/160호 |
| data[].orderItems[].cancelCount | number | 취소 수량 | 0 |
| data[].orderItems[].holdCountForCancel | number | 환불대기 수량 | 0 |
| data[].orderItems[].estimatedShippingDate | string | 주문시 출고예정일 (분리배송 출고예정일) (ISO-8601, `yyyy-mm-dd`) optional | 2017-10-16 |
| data[].orderItems[].plannedShippingDate | string | 실제 출고예정일 (분리배송 시) (yyyy-mm-dd) optional | (빈 문자열) |
| data[].orderItems[].invoiceNumberUploadDate | string | 운송장번호 업로드 일시 (`yyyy-MM-dd'T'HH:mm:ss`) optional | (빈 문자열) |
| data[].orderItems[].extraProperties | object | 업체상품옵션 추가 정보 (key:value) optional | {} |
| data[].orderItems[].pricingBadge | boolean | 최저가 상품 여부 | false |
| data[].orderItems[].usedProduct | boolean | 중고 상품 여부 | false |
| data[].orderItems[].confirmDate | string | 구매확정일자 (`yyyy-MM-dd HH:mm:ss` 또는 ISO-8601) | 2025-01-15T14:17:13.973885-08:00 |
| data[].orderItems[].deliveryChargeTypeName | string | 배송비구분 (유료/무료) | 유료 |
| data[].orderItems[].upBundleVendorItemId | number | 자동생성옵션 ID | (number) |
| data[].orderItems[].upBundleVendorItemName | string | 자동생성옵션 노출상품명 | (string) |
| data[].orderItems[].upBundleSize | number | 자동생성옵션 개수 | (number) |
| data[].orderItems[].upBundleItem | boolean | 자동생성옵션 아이템 여부 | false |
| data[].orderItems[].canceled | boolean | 주문 취소 여부 | false |
| data[].overseaShippingInfoDto | object | 해외배송정보 (optional) | (object) |
| data[].overseaShippingInfoDto.personalCustomsClearanceCode | string | 개인통관 고유부호 (optional) | (string) |
| data[].overseaShippingInfoDto.ordererSsn | string | 미사용 (optional) | (string) |
| data[].overseaShippingInfoDto.ordererPhoneNumber | string | 통관용 수신자 전화번호 (E.164) | (string) |
| data[].deliveryCompanyName | string | 택배사 | CJ 대한통운 |
| data[].invoiceNumber | string | 운송장번호 | 340010913442 |
| data[].inTrasitDateTime | string | 출고일(발송일) (ISO-8601) | 2025-01-15T14:17:13.973885-08:00 |
| data[].deliveredDate | string | 배송완료일 (ISO-8601) | 2025-01-15T14:17:13.973885-08:00 |
| data[].refer | string | 결제위치 (아이폰앱/안드로이드앱/PC웹/모바일웹) | 안드로이드앱 |
| data[].shipmentType | string | 배송유형 (THIRD_PARTY / CGF / CGF LITE) | THIRD_PARTY |
| data[].isCod | boolean | 현금결제(착불/COD) 방식 여부 | false |
| data[].extraProperties | object | 주문 속성 기타 정보 (key:value). taxReceiptInfo / sameDayShipping / cutOffTimeHour 등 포함 | (object) |
| data[].extraProperties.taxReceiptInfo.receiptOption | string | 영수증 옵션. `PAPER` / `E-GUI` | PAPER |
| data[].extraProperties.taxReceiptInfo.appliedType | string | 세금 계산서 유형. `PERSONAL_COUPANG_MEMBER_CARRIER` / `PERSONAL_MOBILE_BARCODE_CARRIER` / `DONATION` / `BUSINESS` | PERSONAL_COUPANG_MEMBER_CARRIER |
| data[].extraProperties.taxReceiptInfo.appliedValue | string | 통합 영수증 번호 (appliedType에 따라 의미 다름; null/모바일 바코드/기부번호/사업자등록번호) | null |
| data[].extraProperties.sameDayShipping | string | 당일 배송 여부 ("true"/"false") | "false" |
| data[].extraProperties.cutOffTimeHour | string | 당일 배송 미적용 시간. 범위 `10~23,0` | "18" |
| nextToken | string | 다음 페이지 요청 토큰. 마지막 페이지면 빈 값 | 448537989 |

### 상태 코드
| 코드 | 의미 |
|---|---|
| 200 | OK |
| 400 | 요청변수확인 — `Invalid vendor ID`, `endTime-startTime range should less than31.` 등 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국, 대만 구매자 사용자만 적용 가능
- 조회 기간 **최대 31일** — 초과 시 `endTime-startTime range should less than31.` 에러
- 날짜 형식: ISO-8601 `yyyy-mm-dd%2B09:00` (`+`는 `%2B`로 URL 인코딩 필수)
- 페이지당 최대 50건 (`maxPerPage`)
- 페이지네이션 cursor(token) 방식 — offset/page 미지원
- **반품완료건은 조회 불가** — `반품/취소 요청 목록 조회` API 사용
- **결제완료 → 상품준비중 처리 후 배송지(`receiver`) 변경 가능성 있음** → 상품준비중 처리 이후 `receiver` 재확인 필수 (`발주서 단건 조회` API 권장)
- **주문 건이 많을 경우 타임아웃 발생 가능** → 클라이언트 측 타임아웃 시간을 늘릴 것
- 출고 전 `sellerProductName + sellerProductItemName`과 `vendorItemName`이 일치하는지 반드시 확인 (구성/수량/용량 불일치 시 출고 보류 + 온라인 문의 접수)
- URL API Name: `GET_ORDERSHEET`

## 에이전트 사용 메모
- **주문 처리 자동화 핵심 API** — 상태별 발주서 조회 → 처리 단계 자동화 (결제완료→상품준비중→송장업로드 등)
- 페이지네이션 패턴:
  1. 첫 호출: `nextToken` 생략 (또는 빈값)
  2. 응답의 `nextToken`이 비어있지 않으면 다음 호출의 `nextToken`으로 사용
  3. `nextToken=""`이면 종료
- **배송지 변경 안전 패턴:** 상품준비중 처리 후 송장 등록 직전에 `발주서 단건 조회`로 `receiver` 재확인
- 가격은 모두 Money 객체(`currencyCode`, `units`, `nanos`) — 단위 계산 시 `nanos`까지 합산
- `productId`는 머지/분리로 변경 가능 → 매핑/대사 key로는 **`vendorItemId`** 사용
- 일별 페이징 vs 분단위 페이징: `searchType=timeFrame` 사용 시 분단위 API로 라우팅됨 (분단위 변경분 수집 목적이면 분단위 API 권장)
- 당일 배송 자동화: `extraProperties.sameDayShipping` + `cutOffTimeHour` 조합으로 판별
- 통관/해외주문: `overseaShippingInfoDto.personalCustomsClearanceCode` 필수 항목 누락 시 출고 전 검증
- 시간대 주의: 응답의 datetime은 `-08:00` 등 오프셋 포함 → KST(`+09:00`)로 변환 후 집계
- 31일 초과 기간 분석: 클라이언트 측에서 31일 단위로 슬라이스해 여러 번 호출
- 엣지 케이스: 한 번의 호출에 결과가 매우 많을 때 타임아웃 → `maxPerPage`를 50 미만으로 낮추거나 클라이언트 타임아웃 증가
- 엣지 케이스: `remotePrice`가 `null`로 응답될 수 있음 (도서산간 아닐 때) → null 가드 필수
