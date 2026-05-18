# 매출내역 조회 — coupang

> 마지막 검증: 2026-05-17
> 상태: 파일럿

매출인식일(구매확정일 or 배송완료 + 7일)을 기준으로 상세한 매출 내역을 조회합니다. 주문 단위로 SALE/REFUND 구분, 배송비 내역, 주문상품별 정산금액(서비스이용료/쿠런티/할인쿠폰 등)이 포함됩니다. 한국 지역 한정 API입니다.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/openapi/apis/api/v1/revenue-history
- 인증: HMAC Signature (쿠팡 Open API 표준 — `Authorization` 헤더에 HMAC 서명 포함)

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | CEA algorithm=HmacSHA256, access-key={ACCESS_KEY}, signed-date={yyMMddTHHmmssZ}, signature={HMAC} — 별도 HMAC Signature 생성 API 참조 |
| Content-Type | N | application/json (본 API는 body 없음 — `not require body`) |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| vendorId | string | Y | 판매자 ID. 쿠팡에서 업체에 발급한 고유 코드 | A00012345 |
| recognitionDateFrom | string | Y | 매출인식 시작일. `YYYY-MM-dd`. recognitionDateTo와 함께 최대 31일 이내 범위 | 2019-10-01 |
| recognitionDateTo | string | Y | 매출인식 종료일. `YYYY-MM-dd`. 전일(어제)까지만 조회 가능 | 2019-10-30 |
| token | string | Y | 다음 페이지 조회용 토큰. 첫 페이지는 `token=`까지만(빈값). 두 번째 페이지부터는 직전 응답의 `nextToken` 사용 | (빈값) 또는 `xxxxxxx` |
| maxPerPage | number | N | 페이지당 최대 호출 개수. 기본값 50, 범위 1–50 | 50 |

### 조회 가능 기간
- 최대: 31일 (`recognitionDateFrom` ~ `recognitionDateTo`)
- 기본값: 없음 (사용자가 명시 필수)
- 종료일 제한: 전일(어제)까지만 — 당일/미래 날짜는 400 오류

### 페이지네이션
- 방식: cursor (token 기반)
- 파라미터: `token`(다음 페이지용) + `maxPerPage`(페이지 크기)
- 최대 size: 50
- 다음 페이지 판단: 응답 `hasNext=true`이면 `nextToken`을 다음 호출 `token`에 사용
- 첫 호출 시 `token=` (빈값)으로 시작

## Response

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| code | number | 서버 응답 코드 | 200 |
| message | string | 상세 메시지 | OK |
| data | array | 결과 리스트. 결과 없을 시 빈 리스트 | [...] |
| data[].orderId | number | 주문번호 | 28000048862315 |
| data[].saleType | string | 항목구분. `SALE`(주문 건) / `REFUND`(반품 건) | SALE |
| data[].saleDate | string | 결제완료일 `YYYY-MM-dd` | 2019-09-06 |
| data[].recognitionDate | string | 매출인식일 `YYYY-MM-dd`. '배송완료+7day' 또는 '구매확정' | 2019-10-02 |
| data[].settlementDate | string | 지급예정일 `YYYY-MM-dd` | 2019-11-21 |
| data[].finalSettlementDate | string | 유보액지급 예정일 `YYYY-MM-dd`. **주 단위 정산에만 사용** | 2019-11-21 |
| data[].deliveryFee | object | 배송비 관련 상세 — amount/fee/feeVat/feeRatio/settlementAmount/baseAmount/baseFee/baseFeeVat/remoteAmount/remoteFee/remoteFeeVat | (object) |
| data[].deliveryFee.amount | number | 총 배송비 (기본배송비 + 도서산간배송비) | 0 |
| data[].deliveryFee.fee | number | 총 배송비 수수료 | 0 |
| data[].deliveryFee.feeVat | number | 총 배송비 부가가치세 | 0 |
| data[].deliveryFee.feeRatio | number | 배송비 수수료율 (%) | 3 |
| data[].deliveryFee.settlementAmount | number | 배송비 정산 대상액 (= 총 배송비 - 수수료 - 부가세) | 0 |
| data[].deliveryFee.baseAmount | number | 기본배송비 | 0 |
| data[].deliveryFee.baseFee | number | 기본배송비 수수료 | 0 |
| data[].deliveryFee.baseFeeVat | number | 기본배송비 부가가치세 | 0 |
| data[].deliveryFee.remoteAmount | number | 도서산간 배송비 | 0 |
| data[].deliveryFee.remoteFee | number | 도서산간 배송비 수수료 | 0 |
| data[].deliveryFee.remoteFeeVat | number | 도서산간 배송비 부가가치세 | 0 |
| data[].items | array | 주문상품별 정산금액 상세 | [...] |
| data[].items[].taxType | string | 과세여부 | TAX |
| data[].items[].productId | number | 노출상품 ID. **머지/분리로 변경될 수 있어 정산 대사 key로 사용 불가** | 294693352 |
| data[].items[].productName | string | 노출상품명 | gtest 테스트 비정품잉크 |
| data[].items[].vendorItemId | number | 옵션 ID. 쿠팡의 가장 작은 상품 단위. **변경되지 않으므로 key로 사용 권장** | 5307184135 |
| data[].items[].vendorItemName | string | 옵션명 | gtest 테스트 비정품잉크, 1개, 블랙 |
| data[].items[].salePrice | number | 총 판매가 (수량 반영) | 300 |
| data[].items[].quantity | number | 수량 | 2 |
| data[].items[].coupangDiscountCoupon | number | 쿠팡지원할인금액 | 0 |
| data[].items[].discountCouponPolicyAgreement | boolean | 쿠팡지원 할인쿠폰 동의여부 | false |
| data[].items[].saleAmount | number | 매출금액 (= 판매액 - 쿠팡지원할인) | 300 |
| data[].items[].sellerDiscountCoupon | number | 판매자할인쿠폰 | 0 |
| data[].items[].downloadableCoupon | number | 다운로드 쿠폰 | 0 |
| data[].items[].serviceFee | number | 서비스 이용료 | 22 |
| data[].items[].serviceFeeVat | number | 서비스 이용 부가가치세 | 2 |
| data[].items[].serviceFeeRatio | number | 서비스이용율 (%, VAT별도) | 7.0 |
| data[].items[].settlementAmount | number | 정산금액 (= 매출금액 - (서비스이용료 + 서비스이용VAT)) | 276 |
| data[].items[].couranteeFeeRatio | number | 쿠런티 이용료 (%) | 0 |
| data[].items[].couranteeFee | number | 쿠런티 이용료 (금액) | 0 |
| data[].items[].couranteeFeeVat | number | 쿠런티 이용 부가가치세 | 0 |
| data[].items[].externalSellerSkuCode | string | 셀러 상품 관리코드 | (빈 문자열 가능) |
| data[].items[].storeFeeDiscount | number | 셀러 스토어 이용료 할인 금액 | 0 |
| data[].items[].storeFeeDiscountVat | number | 셀러 스토어 이용료 부가세 | 0 |
| hasNext | boolean | 다음 페이지 데이터 존재 여부 | false |
| nextToken | string | 다음 페이지 조회용 토큰값 | (빈 문자열 또는 토큰) |

### 상태 코드
| 코드 | 의미 |
|---|---|
| 200 | OK — 정상 응답 |
| 400 | 요청변수확인 — `recognitionDateTo`가 당일/미래, 기간 1달 초과, 필수 파라미터 누락, 날짜 포맷 오류(`yyyy-MM-dd`), token 포맷 오류 등 |

#### 400 오류 메시지 상세
| 오류 메시지 | 해결 방법 |
|---|---|
| `dateTo: 전일까지만 조회할 수 있습니다.` | `recognitionDateTo`에 전일까지만 입력 |
| `dateFrom, dateTo: 1달 이내의 범위로만 조회가능합니다.` | 한달 이내 날짜 범위로 조정 |
| `Required String parameter 'vendorId' is not present` | `vendorId` 입력 확인 |
| `recognitionDateFrom: Invalid format. 'yyyy-MM-dd' 형식을 사용하세요.` | `YYYY-MM-dd` 형식 사용 |
| `recognitionDateTo: Invalid format. 'yyyy-MM-dd' 형식을 사용하세요.` | `YYYY-MM-dd` 형식 사용 |
| `Required String parameter 'token' is not present` | `token` 입력 확인 (첫 페이지는 빈값) |
| `token: Invalid format. 첫 페이지 호출 시에는 비워두세요.` | 첫 페이지는 빈값, 이후는 이전 응답의 `nextToken` 사용 |

## 제약사항
- 호출 한도: 명시 없음 (쿠팡 Open API 공통 정책 적용)
- **지역 제한:** 한국 지역 구매자 사용자만 적용 가능
- 조회 기간 **최대 31일** — 이를 초과하면 400 오류
- 조회 종료일은 **전일(어제)까지만** 허용 — 당일/미래 입력 시 400 오류
- 날짜 포맷 고정: `YYYY-MM-dd`
- 페이지당 최대 50건 (`maxPerPage`)
- 페이지네이션은 cursor 방식(token) — offset/page 지원 안 함
- `finalSettlementDate`는 **주 단위 정산에만 사용** (다른 정산 주기는 의미 없을 수 있음)
- **정산 대사 시 key:** `productId`는 머지/분리로 변경 가능 → key로 사용 금지. **`vendorItemId`**를 정산 대사 key로 사용
- `code`/`message`는 200 OK도 응답 본문에 포함됨 (HTTP 상태와 별개)
- URL API Name: `GET_REVENUE_HISTORY`

## 에이전트 사용 메모
- **월 매출 대시보드/리포팅 에이전트 핵심 API** — 한 달 매출 조회 시 31일 범위 한 번 호출로 처리 가능
- 30일 초과 기간(예: 분기/연간) 조회 시: 31일 단위로 슬라이스해 여러 번 호출 후 클라이언트 측에서 합산
- 페이지네이션 패턴:
  1. 첫 호출: `token=` (빈값)
  2. 응답의 `hasNext`가 true면 `nextToken` 값을 다음 호출의 `token`으로 사용
  3. `hasNext=false` 또는 `nextToken=""`이면 종료
- **정산 대사 자동화**: `vendorItemId`를 key로 사용해 내부 SKU 매핑. `productId`는 표시용으로만
- **SALE/REFUND 분리 집계** 필요: `saleType` 값으로 매출/환불 구분
- 배송비 정산 vs 상품 정산 분리: `deliveryFee.settlementAmount`와 `items[].settlementAmount`는 별도 합산
- 인증 토큰 만료 시 401 발생 가능 → HMAC Signature 재생성 후 재시도
- season_flag: 시즌 매출 집계 직후 본 API 호출 일정 분산 권장 (대량 호출 회피)
- 엣지 케이스: 응답 데이터 중 `orderId=0`인 항목이 존재 — 시스템 차감/조정 등 비주문성 매출인식 데이터로 보임. 집계 시 필터링 또는 별도 카테고리로 분류 고려
- 엣지 케이스: `serviceFeeRatio`가 `null`로 응답되는 항목 존재 → null 처리 로직 필요
- 엣지 케이스: 종료일을 당일로 잘못 보내는 실수 빈발 → 클라이언트에서 어제 날짜로 자동 보정 권장
