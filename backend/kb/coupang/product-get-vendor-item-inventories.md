# 상품 아이템별 수량/가격/상태 조회

## 문서 URL

https://developers.coupangcorp.com/hc/ko/articles/360033645114-%EC%83%81%ED%92%88-%EC%95%84%EC%9D%B4%ED%85%9C%EB%B3%84-%EC%88%98%EB%9F%89-%EA%B0%80%EA%B2%A9-%EC%83%81%ED%83%9C-%EC%A1%B0%ED%9A%8C

## HTTP Method

GET

## Path

/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/inventories

**Example Endpoint**

```
https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/inventories
```

**URL API Name**

GET_PRODUCT_QUANTITY_PRICE_STATUS

---

## Request Parameters

> API 적용 가능한 구매자 사용자 지역: **한국**
>
> 상품 아이템별 재고수량, 판매가격, 판매상태를 조회한다.

### Path Segment Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| vendorItemId | O | Number | 옵션ID — 벤더아이템에 부여되는 고유 번호입니다. |

## Request Body

not require body

---

## Response Message

| Name | Type | Description |
|------|------|-------------|
| code | Number | 결과코드 — SUCCESS/ERROR |
| message | String | 결과 메세지 |
| data | | 조회된 옵션 수량/가격/상태 |
| &nbsp;&nbsp;sellerItemId | Number | 옵션아이디 |
| &nbsp;&nbsp;amountInStock | Number | 옵션잔여수량 |
| &nbsp;&nbsp;salePrice | Number | 옵션판매가격 |
| &nbsp;&nbsp;onSale | Boolean | 옵션판매상태 — true/false |

---

## Response Example

```json
{
  "code": "SUCCESS",
  "message": "",
  "data": {
    "sellerItemId": 3000000000,
    "amountInStock": 0,
    "salePrice": 32000,
    "onSale": true
  }
}
```

---

## Error Response

| HTTP 상태 코드(오류 유형) | 오류 메시지 | 해결 방법 |
|--------------------------|------------|----------|
| 400 (요청변수확인) | 유효한 옵션이 없습니다:[vendorItemId=3039***378] | 옵션ID(vendorItemId) 값을 올바로 입력했는지 확인합니다. 옵션ID(vendorItemId)가 삭제 되었는지 확인합니다. |
| 400 (요청변수확인) | 유효하지 않은 ID가 입력되었습니다. | 옵션ID(vendorItemId) 값을 올바로 입력했는지 확인합니다. |

---

## Enum / 허용값

### code

| 값 | 설명 |
|----|------|
| SUCCESS | 성공 |
| ERROR | 오류 |

### onSale

| 값 | 설명 |
|----|------|
| true | 판매중 |
| false | 판매중지 |

---

## 주의사항

- 확인불가
