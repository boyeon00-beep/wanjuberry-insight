# 발주서 단건 조회(shipmentBoxId)

## 문서 URL

https://developers.coupangcorp.com/hc/ko/articles/360033792854-%EB%B0%9C%EC%A3%BC%EC%84%9C-%EB%8B%A8%EA%B1%B4-%EC%A1%B0%ED%9A%8C-shipmentBoxId

## HTTP Method

GET

## Path

/v2/providers/openapi/apis/api/v5/vendors/{vendorId}/ordersheets/{shipmentBoxId}

**Example Endpoint**

```
https://api-gateway.coupang.com/v2/providers/openapi/apis/api/v5/vendors/A00000001/ordersheets/642538971006401429
```

**URL API Name**

GET_ORDERSHEET_BY_SHIPMENTBOX

---

## Request Parameters

> API 적용 가능한 구매자 사용자 지역: **한국, 대만**
>
> shipmentBoxId를 이용하여 발주서 단건을 조회하는 API입니다.

### Path Segment Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| vendorId | O | | 업체코드 — 쿠팡에서 업체에게 발급한 고유 코드. Wing 로그인 후 확인 가능 |
| shipmentBoxId | O | | 배송번호(묶음배송번호) — Wing 또는 발주서 목록 조회(분단위/일단위)를 통해 조회. shipmentBoxId는 Number type |

## Request Body

not require body

---

## Response Message

| Name | Type | Description |
|------|------|-------------|
| code | Number | 서버 응답 코드 |
| message | String | 서버 응답 메세지 |
| data | Object | |
| &nbsp;&nbsp;shipmentBoxId | Number | 배송번호 |
| &nbsp;&nbsp;orderId | Number | 주문번호 |
| &nbsp;&nbsp;orderedAt | String | 주문일시 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;orderer | Object | 주문자 정보 |
| &nbsp;&nbsp;&nbsp;&nbsp;name | String | 주문자 이름 |
| &nbsp;&nbsp;&nbsp;&nbsp;email | String | 주문자 E-mail — 미사용(빈값) |
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
| &nbsp;&nbsp;parcelPrintMessage | String | 배송메세지 |
| &nbsp;&nbsp;splitShipping | Boolean | 분리배송여부 |
| &nbsp;&nbsp;ableSplitShipping | Boolean | 분리배송가능여부 |
| &nbsp;&nbsp;receiver | Object | 수취인 정보 |
| &nbsp;&nbsp;&nbsp;&nbsp;name | String | 수취인 이름 |
| &nbsp;&nbsp;&nbsp;&nbsp;safeNumber | String | 수취인 연락처(안심번호) (E.164 준수) |
| &nbsp;&nbsp;&nbsp;&nbsp;receiverNumber | String | 수취인 연락처(실전화번호) (E.164 준수) — null |
| &nbsp;&nbsp;&nbsp;&nbsp;addr1 | String | 수취인 배송지1 |
| &nbsp;&nbsp;&nbsp;&nbsp;addr2 | String | 수취인 배송지2 |
| &nbsp;&nbsp;&nbsp;&nbsp;postCode | String | 수취인 우편번호 |
| &nbsp;&nbsp;orderItems | Array | 주문 상품 정보 |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemPackageId | Number | vendorItemPackageId — 미사용 / 없는 경우 0으로 리턴 |
| &nbsp;&nbsp;&nbsp;&nbsp;vendorItemPackageName | String | vendorItemPackageName — 미사용 |
| &nbsp;&nbsp;&nbsp;&nbsp;productId | Number | 노출상품ID — 없는 경우 0으로 리턴 |
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
| &nbsp;&nbsp;&nbsp;&nbsp;externalVendorSkuCode | String | 업체 외부 상품 코드 |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoHeader | String | 상품별 개별 입력 항목 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoValue | String | 상품별 개별 입력 항목에 대한 사용자의 입력값 (optional) — 미사용 |
| &nbsp;&nbsp;&nbsp;&nbsp;etcInfoValues | Array | 상품별 개별 입력 항목에 대한 사용자의 입력값 리스트 (optional) |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductId | Number | 등록상품ID |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductName | String | 등록상품명 |
| &nbsp;&nbsp;&nbsp;&nbsp;sellerProductItemName | String | 등록옵션명 |
| &nbsp;&nbsp;&nbsp;&nbsp;firstSellerProductItemName | String | 최초등록옵션명 |
| &nbsp;&nbsp;&nbsp;&nbsp;cancelCount | Number | 취소수량 |
| &nbsp;&nbsp;&nbsp;&nbsp;holdCountForCancel | Number | 환불대기수량 |
| &nbsp;&nbsp;&nbsp;&nbsp;estimatedShippingDate | String | 주문 시 출고예정일 (ISO-8601) — yyyy-MM-dd |
| &nbsp;&nbsp;&nbsp;&nbsp;plannedShippingDate | String | 실제 출고예정일 (분리배송 시) (ISO-8601) — yyyy-MM-dd |
| &nbsp;&nbsp;&nbsp;&nbsp;invoiceNumberUploadDate | String | 운송장번호 업로드 일시 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;&nbsp;&nbsp;extraProperties | Object | 업체상품옵션 추가 정보 — key:value 형태 |
| &nbsp;&nbsp;&nbsp;&nbsp;pricingBadge | Boolean | 쿠런티(최저가 상품 여부) — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;usedProduct | Boolean | 중고 상품 여부 — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;confirmDate | String | 구매확정일자 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;&nbsp;&nbsp;deliveryChargeTypeName | String | 배송비구분 — 유료, 무료 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleVendorItemId | Number | 자동생성옵션 ID |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleVendorItemName | String | 자동생성옵션 노출상품명 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleSize | Number | 자동생성옵션 개수 |
| &nbsp;&nbsp;&nbsp;&nbsp;upBundleItem | Boolean | 자동생성옵션 아이템 여부 — true/false |
| &nbsp;&nbsp;&nbsp;&nbsp;canceled | Boolean | 주문 취소 여부 — true/false |
| &nbsp;&nbsp;overseaShippingInfoDto | Object | 해외배송정보 |
| &nbsp;&nbsp;&nbsp;&nbsp;personalCustomsClearanceCode | String | 개인통관 고유부호 |
| &nbsp;&nbsp;&nbsp;&nbsp;orderersSsn | String | 미사용(Not in use) |
| &nbsp;&nbsp;&nbsp;&nbsp;ordererPhoneNumber | String | 통관용 수신자 전화번호 (E.164 준수) |
| &nbsp;&nbsp;deliveryCompanyName | String | 택배사 — CJ 대한통운, 한진택배 등 |
| &nbsp;&nbsp;invoiceNumber | String | 운송장번호 |
| &nbsp;&nbsp;inTrasitDateTime | String | 출고일(발송일) (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;deliveredDate | String | 배송완료일 (ISO-8601) — YYYY-MM-DDThh:mm:ss.ssssss±hh:mm |
| &nbsp;&nbsp;refer | String | 결제위치 — 아이폰앱, 안드로이드앱, PC웹 |
| &nbsp;&nbsp;shipmentType | String | 배송유형 — THIRD_PARTY, CGF, CGF LITE |
| &nbsp;&nbsp;isCod | Boolean | 주문이 현금결제(착불/COD) 방식인지 여부 — true/false |
| &nbsp;&nbsp;extraProperties | Object | 주문 속성의 기타 정보 — key:value 형식. receiptOption, appliedType, appliedValue, sameDayShipping, cutOffTimeHour |

---

## Response Example

```json
{
  "code": "200",
  "message": "OK",
  "data": {
    "shipmentBoxId": 64253897***6401429,
    "orderId": 500000596,
    "orderedAt": "2025-01-15T14:17:13.973885-08:00",
    "orderer": {
      "name": "김문근",
      "email": "",
      "safeNumber": "+1(555)444-1234",
      "ordererNumber": null
    },
    "paidAt": "2025-01-15T14:17:13.973885-08:00",
    "status": "FINAL_DELIVERY",
    "shippingPrice": { "currencyCode": "KRW", "units": 2500, "nanos": 0 },
    "remotePrice": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
    "remoteArea": false,
    "parcelPrintMessage": null,
    "splitShipping": false,
    "ableSplitShipping": false,
    "receiver": {
      "name": "test",
      "safeNumber": "+1(555)444-1234",
      "receiverNumber": null,
      "addr1": "addr1",
      "addr2": "addr2",
      "postCode": "284-60"
    },
    "orderItems": [
      {
        "vendorItemPackageId": 0,
        "vendorItemPackageName": "러비더비 섬유향수 보솔레이",
        "productId": 2429,
        "vendorItemId": 3000000177,
        "vendorItemName": "러비더비 섬유향수 보솔레이, 500ml",
        "shippingCount": 1,
        "salesPrice": { "currencyCode": "KRW", "units": 14000, "nanos": 0 },
        "orderPrice": { "currencyCode": "KRW", "units": 14000, "nanos": 0 },
        "discountPrice": { "currencyCode": "KRW", "units": 500, "nanos": 0 },
        "instantCouponDiscount": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
        "downloadableCouponDiscount": { "currencyCode": "KRW", "units": 500, "nanos": 0 },
        "coupangDiscount": { "currencyCode": "KRW", "units": 0, "nanos": 0 },
        "externalVendorSkuCode": "800022867",
        "etcInfoHeader": null,
        "etcInfoValue": null,
        "etcInfoValues": ["추가메시지1", "추가메시지2"],
        "sellerProductId": 26758514,
        "sellerProductName": "[러비더비] 대용량 섬유향수 보솔레이 500ml",
        "sellerProductItemName": "01_보솔레이 500ml",
        "firstSellerProductItemName": "01_보솔레이 500ml",
        "cancelCount": 0,
        "holdCountForCancel": 0,
        "estimatedShippingDate": "2017-10-12",
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
      "personalCustomsClearanceCode": null,
      "ordererSsn": "",
      "ordererPhoneNumber": ""
    },
    "deliveryCompanyName": "CJ 대한통운",
    "invoiceNumber": "337398446274",
    "inTrasitDateTime": "2025-01-15T14:17:13.973885-08:00",
    "deliveredDate": "2025-01-15T14:17:13.973885-08:00",
    "refer": "PC웹",
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
}
```

---

## Error Response

| HTTP 상태 코드(오류 유형) | 오류 메시지 | 해결 방법 |
|--------------------------|------------|----------|
| 400 (요청변수확인) | 해당 주문이 취소 또는 반품되었습니다. | 반품/취소 요청 목록 조회 API를 통해 해당주문의 취소, 반품여부를 확인합니다. 해당 주문을 반복 호출하지 않도록 처리합니다. |
| 400 (요청변수확인) | Invalid vendor ID | 판매자ID(vendorId)를 올바로 입력했는지 확인합니다. |

---

## Enum / 허용값

### status (Response)

| STATUS | MEANING |
|--------|---------|
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

- data가 Object 타입 (목록 조회 API의 Array와 다름) — 단건 응답
- shipmentBoxId는 Number type
- 취소/반품된 주문 조회 시 400 에러 반환 — 반복 호출하지 않도록 처리 필요
- 발주 가능 수량 = shippingCount - (holdCountForCancel + cancelCount)
