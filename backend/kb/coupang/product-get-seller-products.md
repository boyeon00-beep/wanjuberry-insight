# 상품 목록 페이징 조회

## 문서 URL

https://developers.coupangcorp.com/hc/ko/articles/360033645034-%EC%83%81%ED%92%88-%EB%AA%A9%EB%A1%9D-%ED%8E%98%EC%9D%B4%EC%A7%95-%EC%A1%B0%ED%9A%8C

## HTTP Method

GET

## Path

/v2/providers/seller_api/apis/api/v1/marketplace/seller-products

**Example Endpoint**

```
https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/seller-products?vendorId={vendorId}&nextToken={nextToken}&maxPerPage={maxPerSize}&sellerProductId={sellerProductId}&sellerProductName={sellerProductName}&status={status}&manufacture={manufacture}&createdAt={createdAt}&violationTypes=ATTR&violationTypes=MOTA_V2&violationTypeAndOr=OR
```

**URL API Name**

GET_PRODUCTS_BY_QUERY

---

## Request Parameters

> API 적용 가능한 구매자 사용자 지역: **한국, 대만**
>
> 등록상품 목록을 페이징 조회한다.

### Query String Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| vendorId | O | String | 판매자 ID — 쿠팡에서 업체에게 발급한 고유 코드 (예: A00012345) |
| nextToken | | Number | 페이지 — 다음 페이지를 호출하기 위한 키값. 첫 페이지 호출시에는 넣지 않거나 1 입력 |
| maxPerPage | | Number | 페이지당건수 — 기본값: 10, 최대값: 100 |
| sellerProductId | | Number | 등록상품ID |
| sellerProductName | | String | 등록상품명 — 등록상품명 검색. 20자 이하 |
| status | | String | 업체상품상태 (Enum 참고) |
| manufacture | | String | 제조사 |
| createdAt | | String | 상품등록일시 — "yyyy-MM-dd" 형식. 예) 2015-12-17 입력 시 2015-12-17T00:00:00 ~ 2015-12-17T23:59:59로 조회됨 |
| ViolationTypeSearchField | | List | 위반유형 필터 (NO_VA_V2 / MOTA_V2 / ATTR) |
| ViolationTypeAndOr | | String | ViolationTypeSearchField에 2개 이상 입력 시 필수. 값: AND / OR |

## Request Body

not require body

---

## Response Message

| Name | Type | Description |
|------|------|-------------|
| code | Number | 결과코드 — SUCCESS/ERROR |
| message | String | 결과 메세지 |
| nextToken | String | 다음페이지 — 다음 페이지가 없을 경우 빈문자열 |
| data | Array | |
| &nbsp;&nbsp;sellerProductId | String | 등록상품ID |
| &nbsp;&nbsp;sellerProductName | String | 등록상품명 |
| &nbsp;&nbsp;displayCategoryCode | Number | 노출카테고리코드 |
| &nbsp;&nbsp;categoryId | Number | 카테고리아이디 |
| &nbsp;&nbsp;productId | Number | ProductID |
| &nbsp;&nbsp;vendorId | String | 판매자ID |
| &nbsp;&nbsp;saleStartedAt | String | 판매시작일시 — "yyyy-MM-ddTHH:mm:ss" 형식 |
| &nbsp;&nbsp;saleEndedAt | String | 판매종료일시 — "yyyy-MM-ddTHH:mm:ss" 형식 |
| &nbsp;&nbsp;brand | String | 브랜드 |
| &nbsp;&nbsp;statusName | String | 등록상품상태 (Enum 참고) |
| &nbsp;&nbsp;createdAt | String | 판매등록일시 — "yyyy-MM-ddTHH:mm:ss" 형식 |

---

## Response Example

```json
{
  "code": "SUCCESS",
  "message": "",
  "nextToken": "2",
  "data": [
    {
      "sellerProductId": 239092172,
      "sellerProductName": "R07 헬로키티 미니낚시놀이",
      "displayCategoryCode": 77413,
      "categoryId": 2102,
      "productId": 14784194,
      "vendorId": "XXXXXXXX",
      "mdId": "harry867@",
      "mdName": null,
      "saleStartedAt": "2017-02-14T06:00:00",
      "saleEndedAt": "2099-12-31T00:00:00",
      "brand": "상세설명별도참조",
      "statusName": "승인완료",
      "createdAt": "2017-02-13T02:09:47"
    },
    {
      "sellerProductId": 239092161,
      "sellerProductName": "R07 러닝리소스 손가락 지시봉 (10개 세트) (LER2657) - 러닝리소스 지시봉 손가락 포인터 장난감",
      "displayCategoryCode": 77413,
      "categoryId": 2102,
      "productId": 14784126,
      "vendorId": "XXXXXXXX",
      "mdId": "harry867@",
      "mdName": null,
      "saleStartedAt": "2017-02-14T06:00:00",
      "saleEndedAt": "2099-12-31T00:00:00",
      "brand": "상세설명별도참조",
      "statusName": "승인완료",
      "createdAt": "2017-02-13T02:09:46"
    }
  ]
}
```

---

## Error Response

| HTTP 상태 코드(오류 유형) | 오류 메시지 | 해결 방법 |
|--------------------------|------------|----------|
| 400 (요청변수확인) | 업체코드는 반드시 입력되어야 합니다. | 판매자 ID(vendorId) 값을 올바로 입력했는지 확인합니다. |
| 400 (요청변수확인) | Format of createdAt is `yyyy-MM-dd` | 상품등록일시(createdAt) 값을 "yyyy-MM-dd" 형식으로 입력했는지 확인합니다. |

---

## Enum / 허용값

### status (Request) / statusName (Response)

| Parameter Name | Status |
|----------------|--------|
| IN_REVIEW | 심사중 |
| SAVED | 임시저장 |
| APPROVING | 승인대기중 |
| APPROVED | 승인완료 |
| PARTIAL_APPROVED | 부분승인완료 |
| DENIED | 승인반려 |
| DELETED | 상품삭제 |

### ViolationTypeSearchField

| 값 | 설명 |
|----|------|
| NO_VA_V2 | 상품정보 검증이 필요한 상품 (노출제한) |
| MOTA_V2 | 누락된 필수 구매옵션을 입력해야하는 상품 (노출제한) |
| ATTR | 옵션 수정이 필요한 상품 (노출낮음) |

### ViolationTypeAndOr

| 값 | 설명 |
|----|------|
| AND | 모든 조건 충족 |
| OR | 하나 이상 조건 충족 |

---

## 주의사항

- sellerProductName 검색은 20자 이하로 입력
- createdAt은 "yyyy-MM-dd" 형식으로 입력하면 해당 일자의 00:00:00 ~ 23:59:59 범위로 조회됨
- ViolationTypeAndOr는 ViolationTypeSearchField에 2개 이상 파라미터 입력 시 필수
