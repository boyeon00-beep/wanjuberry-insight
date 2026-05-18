# 지급내역 조회 — coupang

> 마지막 검증: 2026-05-18
> 상태: 파일럿

매출인식월을 기준으로 지급 확정/예정된 내역을 확인합니다. 한국 지역 한정 API.

## Endpoint
- Method: GET
- URL: https://api-gateway.coupang.com/v2/providers/marketplace_openapi/apis/api/v1/settlement-histories
- 인증: HMAC Signature

## Request

### Headers
| 헤더명 | 필수 | 값 |
|---|---|---|
| Authorization | Y | HMAC Signature |

### Query Parameters / Body
| 파라미터 | 타입 | 필수 | 설명 | 예시값 |
|---|---|---|---|---|
| revenueRecognitionYearMonth | string | Y | 매출인식월. 형식 `YYYY-MM`. **당월까지만 조회 가능** | 2019-10 |

(body 없음)

### 조회 가능 기간
- 최대: 1개월 단위
- 기본값: 없음
- **당월 이후는 조회 불가** (해당월까지만)

### 페이지네이션
- 방식: 없음 (해당 월의 모든 지급내역을 배열로 반환)
- 파라미터: -
- 최대 size: -

## Response

응답 본문은 **배열 직접 반환** (래퍼 객체 없음).

### 주요 필드
| 필드명 | 타입 | 설명 | 예시값 |
|---|---|---|---|
| [].settlementType | string | 정산 유형 (`MONTHLY` 월 정산 / `WEEKLY` 주 정산 / `ADDITIONAL` 추가 지급 / `RESERVE` 최종액 지급. 예시에는 `DAILY`도 출현) | DAILY |
| [].settlementDate | string | 정산(예정)일 | 2019-10-10 |
| [].revenueRecognitionYearMonth | string | 매출인식월 | 2019-10 |
| [].revenueRecognitionDateFrom | string | 매출인식 시작일 | 2019-10-01 |
| [].revenueRecognitionDateTo | string | 매출인식 종료일 | 2019-10-01 |
| [].totalSale | number | 총판매액 (= 판매액 + 판매배송료 - (취소액 + 취소배송료 + 할인쿠폰)) | 58150 |
| [].serviceFee | number | 판매수수료 (= 판매수수료 + 우대수수료 환급액) | 8782 |
| [].settlementTargetAmount | number | 정산 대상액 (= 총판매액 - 판매수수료) | 39368 |
| [].settlementAmount | number | 지급액 (주정산 = 대상액 70%, 월정산 = 대상액 100%) | 39368 |
| [].lastAmount | number | 최종액 (유보 성격, 주정산 30% 유보금액) | 0 |
| [].pendingReleasedAmount | number | 보류(해제) 금액. 보류 해제되며 이번 지급에 포함될 금액 | 0 |
| [].sellerDiscountCoupon | number | 판매자 할인쿠폰 (즉시할인쿠폰) | 0 |
| [].downloadableCoupon | number | 판매자 할인쿠폰 (다운로드 쿠폰) | 0 |
| [].dedicatedDeliveryAmount | number | 전담택배비 (**사용 안함**) | 0 |
| [].sellerServiceFee | number | 판매자 서비스 이용료 (서버 이용료) | 0 |
| [].couranteeFee | number | 쿠런티 이용료 | 0 |
| [].couranteeCustomerReward | number | 쿠런티 보상금 | 0 |
| [].deductionAmount | number | 정산 차감 | 0 |
| [].debtOfLastWeek | number | 전주 채권 (전주에 발생한 손실 관련 차감액) | 0 |
| [].finalAmount | number | 최종 지급액 or 지급 예정액 (= 지급액 + 보류해제금액 - (전담택배비 + 판매자서비스이용료 + 정산차감 + 전주채권 + 쿠런티이용료 + 쿠런티보상금 + 판매자할인쿠폰 + 스토어이용료할인금액)) | 39368 |
| [].bankAccountHolder | string | 예금주 (마스킹된 형태로 응답) | MASKED |
| [].bankName | string | 은행명 (마스킹된 형태로 응답) | MASKED |
| [].bankAccount | string | 정산대금 입금 계좌번호 (**뒤 4자리 마스킹 처리**) | 100560**** |
| [].status | string | 지급 상태 (`DONE` 지급 완료 / `SUBJECT` 지급 예정) | DONE |
| [].storeFeeDiscount | number | 셀러 스토어 이용료 할인 금액 | 0 |

### 상태 코드
| 코드 | 오류 메시지 | 해결 |
|---|---|---|
| 200 | OK | - |
| 400 | Invalid revenueRecognitionYearMonth format (yyyy-MM) | `yyyy-MM` 형식 확인 |
| 400 | 해당월까지만 조회할 수 있습니다. | 당월 이후 불가 |

## 제약사항
- 호출 한도: 명시 없음
- **지역 제한:** 한국
- 매출인식월(`revenueRecognitionYearMonth`)은 `YYYY-MM` 형식 필수
- **당월까지만 조회 가능** — 미래월 입력 시 400
- 응답은 **배열 직접 반환** (다른 API의 `{code, message, data}` 래퍼와 다름)
- 계좌번호(`bankAccount`)는 서버 측에서 뒤 4자리 마스킹 처리
- 예금주(`bankAccountHolder`)/은행명(`bankName`)도 마스킹 형태로 응답
- 정산 정책:
  - 주정산(WEEKLY): 정산대상액의 70% 지급, 30%는 `lastAmount`로 유보
  - 월정산(MONTHLY): 정산대상액의 100% 지급
- `finalAmount`가 실제 셀러 입금액
- URL API Name: `SETTLEMENT_HISTORIES`

## 에이전트 사용 메모
- **월간 정산 대시보드/현금흐름 예측 에이전트 핵심 API** — 한 달 지급 예정액/완료액 확인
- 한 달 매출에 대한 실수령액 계산: `finalAmount` 합산
- 매출(`revenue-history`)과 지급(본 API)의 페어: 매출인식일 기반으로 매칭 분석 가능
- 차감 분석: `deductionAmount` + `debtOfLastWeek` + 각종 fee를 분리 집계해 손익 가시화
- 주정산 유보분 추적: `lastAmount` 합산으로 미수령 30% 파악, 다음 정산 회차에서 해제 확인
- 보류 해제 금액 알림: `pendingReleasedAmount > 0`이면 이전 보류분이 해제된 것 → 알림 트리거
- season_flag: 시즌 종료 직후 다음 달 정산 예측에 본 API 활용 (당월 매출 → 차월 지급)
- 응답이 배열 직접 — 다른 API와 파서 분리 또는 unify wrapper 처리
- 엣지 케이스: `settlementType`에 문서 미기재 값(`DAILY`)이 응답에 등장 → enum 검증 시 alert 만 띄우고 통과
- 엣지 케이스: `dedicatedDeliveryAmount`는 "사용 안함"으로 명시 — 무시 가능
- 엣지 케이스: 계좌번호가 이미 마스킹된 형태로 응답되므로 추가 마스킹 불필요 (그대로 저장 OK)
