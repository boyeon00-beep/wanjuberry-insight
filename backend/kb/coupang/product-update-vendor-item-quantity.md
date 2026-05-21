# 상품 아이템별 수량 변경

## 문서 URL

https://developers.coupangcorp.com/hc/ko/articles/360034156253-%EC%83%81%ED%92%88-%EC%95%84%EC%9D%B4%ED%85%9C%EB%B3%84-%EC%88%98%EB%9F%89-%EB%B3%80%EA%B2%BD

## HTTP Method

PUT

## Path

/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/quantities/{quantity}

**Example Endpoint**

```
https://api-gateway.coupang.com/v2/providers/seller_api/apis/api/v1/marketplace/vendor-items/{vendorItemId}/quantities/{quantity}
```

**URL API Name**

UPDATE_PRODUCT_QUANTITY_BY_ITEM

---

## Request Parameters

> API 적용 가능한 구매자 사용자 지역: **한국**
>
> 상품 아이템별 재고수량을 변경한다. 이 기능은 판매요청 신청 후 승인완료되어 옵션ID(vendorItemId)가 발급되면 사용할 수 있다.

### Path Segment Parameter

| Name | Required | Type | Description |
|------|----------|------|-------------|
| vendorItemId | O | Number | 옵션ID — 벤더아이템에 부여되는 고유 번호입니다. |
| quantity | O | Number | 재고수량 |

## Request Body

not require body

---

## Response Message

| Name | Type | Description |
|------|------|-------------|
| code | | 결과코드 — SUCCESS/ERROR |
| message | String | 결과 메세지 |

---

## Response Example

```json
{
  "code": "SUCCESS",
  "message": "재고 변경을 완료했습니다."
}
```

---

## Error Response

| HTTP 상태 코드(오류 유형) | 오류 메시지 | 해결 방법 |
|--------------------------|------------|----------|
| 400 (요청변수확인) | 유효하지 않은 재고수량입니다. | 올바른 재고수량(quantity) 값을 입력했는지 확인합니다. |
| 400 (요청변수확인) | 재고변경에 실패했습니다. [옵션ID[3048***251] : 삭제된 상품은 변경이 불가능합니다.] | 옵션ID(vendorItemId)가 삭제 되었는지 확인합니다. |
| 400 (요청변수확인) | 재고변경에 실패했습니다. [vendoritemid 3047***045 not found] | 옵션ID(vendorItemId) 값을 올바로 입력했는지 확인합니다. |

---

## Enum / 허용값

확인불가

---

## 주의사항

- 판매요청 신청 후 승인완료되어 옵션ID(vendorItemId)가 발급된 상품에서만 사용 가능
