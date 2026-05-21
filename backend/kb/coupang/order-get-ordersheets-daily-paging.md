# 발주서 목록 조회(일단위 페이징)

## 문서 URL

https://developers.coupangcorp.com/hc/ko/articles/360033919573-%EB%B0%9C%EC%A3%BC%EC%84%9C-%EB%AA%A9%EB%A1%9D-%EC%A1%B0%ED%9A%8C-%EC%9D%BC%EB%8B%A8%EC%9C%84-%ED%8E%98%EC%9D%B4%EC%A7%95

## HTTP Method

GET

## Path

/v2/providers/openapi/apis/api/v5/vendors/{vendorId}/ordersheets

**Example Endpoint**

```
https://api-gateway.coupang.com/v2/providers/openapi/apis/api/v5/vendors/A00012345/ordersheets?createdAtFrom=2025-07-15%2B09:00&createdAtTo=2025-07-25%2B09:00&maxPerPage=50&status=INSTRUCT
```

**URL API Name**

GET_ORDERSHEETS

---

## Request Parameters

> API 적용 가능한 구매자 사용자 지역: **한국, 대만**
>
> 발주서 목록을 하루단위 페이징 형태로 조회합니다. 예) (2020-02-01 ~ 2020-02-03)
> 페이지당 row사이즈 조정은 maxPerPage 파라미터를 통해 가능하며 다음 페이지는 [nextToken]을 이용하여 얻을 수 있습니다. Path Parameter 일부 제외, 발주서 목록 조회(분 단위 전체)와 전반적으로 구성이 같습니다.

### Path Segment Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| vendorId | O | String | 판매자 ID — 쿠팡에서 업체에게 발급한 고유 코드 (예: A00012345) |

### Query String Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| createdAtFrom | O | String | 검색 시작일시 (ISO-8601 준수) — "yyyy-mm-dd%2B09:00" 형태. 예) 2025-07-01%2B09:00 |
| createdAtTo | O | String | 검색 종료일시 (ISO-8601 준수) — "yyyy-mm-dd%2B09:00" 형태. 예) 2025-07-31%2B09:00. 최대 31일까지 조회 가능 |
| status | O | String | 발주서 상태 (Enum 참고) |
| nextToken | | String | 다음 페이지 조회를 위한 token값. 첫번째 페이지 조회시에는 필요하지 않습니다. 페이지당 최대 50개까지 요청되므로, 이후 페이지를 조회하기 위해서는 [nextToken] 사용 필요 |
| maxPerPage | | Number | 페이지당 최대 조회 요청 값 — default = 50 |
| searchType | | String | search type for order sheets results. searchType=timeFrame이면 발주서 목록 조회(분단위 전체)로 수행되며, 그 외에는 발주서 목록 조회(일단위 페이징)로 수행됩니다. |

## Request Body

not require body

---

## Response Message

| Name | Type | Description |
|------|------|-------------|
| code | Number | 서버 응답 코드 |
| message | String | 서버 응답 메세지 |
| data | Array | 결과리스트 — 결과가 없을 때는 빈 리스트가 리턴 |
| &nbsp;&nbsp;shipmentBoxId | Number | 배송번호(묶음배송번호) |
| &nbsp;&nbsp;orderId | Number | 주문번호 |
| &nbsp;&nbsp;orderedAt | String | 주문일시 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;orderer | Object | 주문자 |
| &nbsp;&nbsp;&nbsp;&nbsp;name | String | 주문자 이름 |
| &nbsp;&nbsp;&nbsp;&nbsp;email | String | 주문자 email — 미사용(빈값) |
| &nbsp;&nbsp;&nbsp;&nbsp;safeNumber | String | 수취인 연락처(안심번호) (E.164 준수) |
| &nbsp;&nbsp;&nbsp;&nbsp;ordererNumber | String | 주문자 연락처(실전화번호) (E.164 준수) — null |
| &nbsp;&nbsp;paidAt | String | 결제일시 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;status | String | 발주서 상태 (Enum 참고) |
| &nbsp;&nbsp;shippingPrice | Object | 배송비 |
| &nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;remotePrice | Object | 도서산간배송비 |
| &nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;remoteArea | Boolean | 도서산간여부 |
| &nbsp;&nbsp;parcelPrintMessage | String | 배송메세지 (optional) |
| &nbsp;&nbsp;splitShipping | Boolean | 분리배송여부 |
| &nbsp;&nbsp;ableSplitShipping | Boolean | 분리배송가능여부 |
| &nbsp;&nbsp;receiver | Object | |
| &nbsp;&nbsp;&nbsp;&nbsp;name | String | 수취인 이름 |
| &nbsp;&nbsp;&nbsp;&nbsp;safeNumber | String | 수취인 연락처(안심번호) (E.164 준수) |
| &nbsp;&nbsp;&nbsp;&nbsp;receiverNumber | String | 수취인 연락처(실전화번호) (E.164 준수) |
| &nbsp;&nbsp;&nbsp;&nbsp;addr1 | String | 수취인 배송지1 |
| &nbsp;&nbsp;&nbsp;&nbsp;addr2 | String | 수취인 배송지2 |
| &nbsp;&nbsp;&nbsp;&nbsp;postCode | String | 수취인 우편번호 |
| &nbsp;&nbsp;orderItems | Array | Items to deliver |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemPackageId | Number | vendorItemPackageId — 미사용 / 없는 경우 0으로 리턴 |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemPackageName | String | vendorItemPackageName — 미사용 |
| &nbsp;&nbsp;&nbsp;&nbsp;productId | Number | productId — optional / 없는 경우 0으로 리턴 |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemId | Number | 옵션ID |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemName | String | 노출상품명 |
| &nbsp;&nbsp;&nbsp;&nbsp;shippingCount | Number | shippingCount = 주문시 item의 구매 수량. holdCountForCancel = 취소가 되어 환불 예정인 수량. cancelCount = 취소가 확정된 수량. 발주 가능 수량 = shippingCount - (holdCountForCancel + cancelCount) |
| &nbsp;&nbsp;&nbsp;&nbsp;salesPrice | Object | 개당 상품 가격(price of one item) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;orderPrice | Object | 결제 가격: salesPrice * shippingCount |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;discountPrice | Object | 총 할인 가격 — discountPrice = instantCouponDiscount + downloadableCoupon + coupangDiscount |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;instantCouponDiscount | Object | 즉시할인 쿠폰 할인 금액 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;downloadableCouponDiscount | Object | 다운로드 쿠폰 할인 금액 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;coupangDiscount | Object | 쿠팡 지원 할인 — 쿠팡 지원 장바구니/카테고리 쿠폰 등의 금액 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;currencyCode | String | 통화 코드 (ISO-4217 준수), 대문자 3개 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;units | Number | 통화 정수 부분, 64 bit |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nanos | Number | 통화 소수점 부분, 32 bit, 값 범위 [-9999999999, 999999999] |
| &nbsp;&nbsp;&nbsp;&nbsp;externalVendorSkuCode | String | external code (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoHeader | String | 상품별 개별 입력 항목 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoValue | String | 상품별 개별 입력 항목에 대한 사용자의 입력값 (optional) — 필드는 존재하나 값이 없는 상태. 필요시 etcInfoValues 사용 |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoValues | Array | 상품별 개별 입력 항목에 대한 사용자의 입력값 리스트 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductId | Number | 등록상품ID |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductName | String | 등록상품명 |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductItemName | String | 등록옵션명 |
| &nbsp;&nbsp;&nbsp;&nbsp;firstSellerProductItemName | String | 최초등록옵션명 |
| &nbsp;&nbsp;&nbsp;&nbsp;cancelCount | Number | 취소수량 |
| &nbsp;&nbsp;&nbsp;&nbsp;holdCountForCancel | Number | 환불대기수량 |
| &nbsp;&nbsp;&nbsp;&nbsp;estimatedShippingDate | String | 주문시 출고예정일 (불리배송 출고예정일) (ISO-8601, optional) — yyyy-mm-dd |
| &nbsp;&nbsp;&nbsp;&nbsp;plannedShippingDate | String | 실제 출고예정일 (분리배송 시) (ISO-8601, optional) — yyyy-mm-dd |
| &nbsp;&nbsp;&nbsp;&nbsp;invoiceNumberUploadDate | String | 운송장번호 업로드 일시 (ISO-8601, optional) — yyyy-MM-dd'T'HH:mm:ss |
| &nbsp;&nbsp;&nbsp;&nbsp;extraProperties | Object | 업체상품옵션 추가 정보 (optional) — key:value 형태 |
| &nbsp;&nbsp;&nbsp;&nbsp;pricingBadge | Boolean | 최저가 상품 여부 — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;usedProduct | Boolean | 중고 상품 여부 — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;confirmDate | String | 구매확정일자 (ISO-8601) — yyyy-MM-dd HH:mm:ss |
| &nbsp;&nbsp;&nbsp;&nbsp;deliveryChargeTypeName | String | 배송비구분 — 유료, 무료 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleVendorItemId | Number | 자동생성옵션 ID |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleVendorItemName | String | 자동생성옵션 노출상품명 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleSize | Number | 자동생성옵션 개수 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleItem | Boolean | 자동생성옵션 아이템 여부 — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;canceled | Boolean | 주문 취소 여부 — true/false |
| &nbsp;&nbsp;overseaShippingInfoDto | Object | 해외배송정보 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;personalCustomsClearanceCode | String | 개인통관 고유부호 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;orderersSsn | String | 미사용 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;ordererPhoneNumber | String | 통관용 수신자 전화번호 (E.164 준수) |
| &nbsp;&nbsp;deliveryCompanyName | String | 택배사 — CJ 대한통운, 한진택배 |
| &nbsp;&nbsp;invoiceNumber | String | 운송장번호 |
| &nbsp;&nbsp;inTrasitDateTime | String | 출고일(발송일) (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;deliveredDate | String | 배송완료일 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;refer | String | 결제위치 — 아이폰앱, 안드로이드앱, PC웹, 모바일웹 |
| &nbsp;&nbsp;shipmentType | String | 배송유형 — THIRD_PARTY, CGF, CGF LITE |
| &nbsp;&nbsp;isCod | Boolean | 주문이 현금결제(착불/COD) 방식인지 여부 — true/false |
| &nbsp;&nbsp;extraProperties | Object | 주문 속성의 기타 정보 — key:value 형식. 세금 계산서(인보이스) 발행 지원 마켓에서 receiptOption, appliedType, appliedValue 표시. sameDayShipping(당일 배송 여부), cutOffTimeHour(당일배송 미적용 시간) |
| nextToken | String | 다음 페이지 요청 전송시 필요한 token 값 — 마지막 페이지인 경우 빈 값으로 리턴 |

---

## Response Example

```json
{
  "code": 200,
  "message": "OK",
  "data": [
    {
      "shipmentBoxId": 64253897***6401429,
      "orderId": 22000009546234,
      "orderedAt": "2025-01-15T14:17:13.973885-08:00",
      "orderer": {
        "name": "신*희",
        "email": "",
        "safeNumber": " +1(555)444-1234",
        "ordererNumber": null
      },
      "paidAt": "2025-01-15T14:17:13.973885-08:00",
      "status": "FINAL_DELIVERY",
      "shippingPrice": { "currencyCode": "KRW", "units": 5000, "nanos": 0 },
      "remotePrice": null,
      "remoteArea": false,
      "parcelPrintMessage": "문 앞",
      "splitShipping": false,
      "ableSplitShipping": false,
      "receiver": {
        "name": "신*희",
        "safeNumber": " +1(555)444-1234",
        "receiverNumber": null,
        "addr1": "경기 오산시 가수동 **아파트",
        "addr2": "109동 *호",
        "postCode": "447-700"
      },
      "orderItems": [
        {
          "vendorItemPackageId": 0,
          "vendorItemPackageName": "인디고뱅크키즈 기모 테잎배색 트레이닝 팬츠 IKTM17WG1",
          "productId": 31846051,
          "vendorItemId": 3242596358,
          "vendorItemName": "인디고뱅크키즈 기모 테잎배색 트레이닝 팬츠 IKTM17WG1, 07 DARK GREY, 160호",
          "shippingCount": 1,
          "salesPrice": { "currencyCode": "KRW", "units": 19000, "nanos": 0 },
          "orderPrice": { "currencyCode": "KRW", "units": 19000, "nanos": 0 },
          "discountPrice": { "currencyCode": "KRW", "units": 3000, "nanos": 0 },
          "instantCouponDiscount": { "currencyCode": "KRW", "units": 2000, "nanos": 0 },
          "downloadableCouponDiscount": { "currencyCode": "KRW", "units": 1000, "nanos": 0 },
          "coupangDiscount": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
          "externalVendorSkuCode": "170816368810",
          "etcInfoHeader": null,
          "etcInfoValue": null,
          "etcInfoValues": ["추가메시지1", "추가메시지2"],
          "sellerProductId": 80240831,
          "sellerProductName": "인디고뱅크키즈 A5 기모 배색츄키니 IKTM17WG1",
          "sellerProductItemName": "07 DARK GREY 160호",
          "firstSellerProductItemName": "07 DARK GREY/160호",
          "cancelCount": 0,
          "holdCountForCancel": 0,
          "estimatedShippingDate": "2017-10-16",
          "plannedShippingDate": "",
          "invoiceNumberUploadDate": "",
          "extraProperties": {},
          "pricingBadge": false,
          "usedProduct": false,
          "confirmDate": "2025-01-15T14:17:13.973885-08:00",
          "deliveryChargeTypeName": "유료",
          "canceled": false
        }
      ],
      "overseaShippingInfoDto": {
        "personalCustomsClearanceCode": "",
        "ordererSsn": "",
        "ordererPhoneNumber": ""
      },
      "deliveryCompanyName": "CJ 대한통운",
      "invoiceNumber": "340010913442",
      "inTrasitDateTime": "2025-01-15T14:17:13.973885-08:00",
      "deliveredDate": "2025-01-15T14:17:13.973885-08:00",
      "refer": "안드로이드앱",
      "shipmentType": "THIRD_PARTY",
      "isCod": false,
      "extraProperties": {
        "sameDayShipping": "false",
        "cutOffTimeHour": "0"
      }
    },
    {
      "shipmentBoxId": 64253897***6401428,
      "orderId": 22000009546630,
      "orderedAt": "2025-01-15T14:17:13.973885-08:00",
      "orderer": {
        "name": "김*숙",
        "email": "hs*****@na",
        "safeNumber": " +1(555)444-1234",
        "ordererNumber": null
      },
      "paidAt": "2025-01-15T14:17:13.973885-08:00",
      "status": "FINAL_DELIVERY",
      "shippingPrice": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
      "remotePrice": null,
      "remoteArea": false,
      "parcelPrintMessage": "직접 받고 부재 시 문 앞",
      "splitShipping": false,
      "ableSplitShipping": false,
      "receiver": {
        "name": "김*숙",
        "safeNumber": " +1(555)444-1234",
        "receiverNumber": null,
        "addr1": "경기 광명시 하안1동 두산트레지움아파트",
        "addr2": "107동701호",
        "postCode": "423-747"
      },
      "orderItems": [
        {
          "vendorItemPackageId": 0,
          "vendorItemPackageName": "리틀브렌 후드달이 구스 경량 점퍼 LBJD17WG5",
          "productId": 34047877,
          "vendorItemId": 3261300431,
          "vendorItemName": "리틀브렌 후드달이 구스 경량 점퍼 LBJD17WG5, 04 MIDDLE MELANGE GR, 170호",
          "shippingCount": 1,
          "salesPrice": { "currencyCode": "KRW", "units": 27800, "nanos": 0 },
          "orderPrice": { "currencyCode": "KRW", "units": 278000, "nanos": 0 },
          "discountPrice": { "currencyCode": "KRW", "units": 2470, "nanos": 0 },
          "instantCouponDiscount": { "currencyCode": "KRW", "units": 560, "nanos": 0 },
          "downloadableCouponDiscount": { "currencyCode": "KRW", "units": 1910, "nanos": 0 },
          "coupangDiscount": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
          "externalVendorSkuCode": "170824416510",
          "etcInfoHeader": null,
          "etcInfoValue": null,
          "etcInfoValues": ["추가메시지1", "추가메시지2"],
          "sellerProductId": 87037167,
          "sellerProductName": "리틀브렌 후드달이 구스 경량 점퍼 LBJD17WG5",
          "sellerProductItemName": "04 MIDDLE MELANGE GR 170호",
          "firstSellerProductItemName": "04 MIDDLE MELANGE GR/170호",
          "cancelCount": 0,
          "holdCountForCancel": 0,
          "estimatedShippingDate": "2017-10-16",
          "plannedShippingDate": "",
          "invoiceNumberUploadDate": "",
          "extraProperties": {},
          "pricingBadge": false,
          "usedProduct": false,
          "confirmDate": "2025-01-15T14:17:13.973885-08:00",
          "deliveryChargeTypeName": "무료",
          "canceled": false
        }
      ],
      "overseaShippingInfoDto": {
        "personalCustomsClearanceCode": "",
        "ordererSsn": "",
        "ordererPhoneNumber": ""
      },
      "deliveryCompanyName": "CJ 대한통운",
      "invoiceNumber": "340010912565",
      "inTrasitDateTime": "2025-01-15T14:17:13.973885-08:00",
      "deliveredDate": "2025-01-15T14:17:13.973885-08:00",
      "refer": "안드로이드앱",
      "shipmentType": "CGF LITE",
      "isCod": false,
      "extraProperties": {
        "taxReceiptInfo": {
          "appliedValue": null,
          "receiptOption": "PAPER",
          "appliedType": "PERSONAL_COUPANG_MEMBER_CARRIER"
        },
        "sameDayShipping": "true",
        "cutOffTimeHour": "18"
      }
    }
  ],
  "nextToken": "448537989"
}
```

---

## Error Response

| HTTP 상태 코드(오류 유형) | 오류 메시지 | 해결 방법 |
|--------------------------|------------|----------|
| 400 (요청변수확인) | Invalid vendor ID | 올바른 판매자 ID(vendorId)를 입력했는지 확인합니다. 예) A00012345 |
| 400 (요청변수확인) | endTime-startTime range should less than31. | 조회기간이 31일 이내인지 확인합니다. |

---

## Enum / 허용값

### status (Request / Response)

| Parameter Name | Status |
|----------------|--------|
| ACCEPT | 결제완료 |
| INSTRUCT | 상품준비중 |
| DEPARTURE | 배송지시 |
| DELIVERING | 배송중 |
| FINAL_DELIVERY | 배송완료 |
| NONE_TRACKING | 업체 직접 배송(배송 연동 미적용), 추적불가 |

### shipmentType (Response)

| 값 | 설명 |
|----|------|
| THIRD_PARTY | 확인불가 |
| CGF | 확인불가 |
| CGF LITE | 확인불가 |

### extraProperties.receiptOption (Response)

| 값 | 설명 |
|----|------|
| PAPER | 종이 영수증 (Paper Invoice) |
| E-GUI | 전자 영수증 (Electronic Invoice) |

### extraProperties.appliedType (Response)

| 값 | 설명 |
|----|------|
| PERSONAL_COUPANG_MEMBER_CARRIER | 쿠팡 회원 매개체 |
| PERSONAL_MOBILE_BARCODE_CARRIER | 휴대폰 바코드 매개체 |
| DONATION | 영수증 기부 |
| BUSINESS | 사업자 영수증 |

---

## 주의사항

- createdAtFrom / createdAtTo는 ISO-8601 표준 준수, "yyyy-mm-dd%2B09:00" 형태로 입력
- 조회 기간은 최대 31일까지 가능
- 페이지당 최대 50건, 다음 페이지는 응답의 nextToken 값을 사용
- searchType=timeFrame 입력 시 발주서 목록 조회(분단위 전체) 방식으로 동작
- etcInfoValue는 필드는 존재하나 값이 없는 상태 — 필요 시 etcInfoValues 배열 사용
- 발주 가능 수량 = shippingCount - (holdCountForCancel + cancelCount)
