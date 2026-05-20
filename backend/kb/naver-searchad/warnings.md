# API 문서 불일치 / 경고 사항

> 화면에서 확인한 내용 기준으로 기록합니다.  
> 수집 대상: AdExtension, Adgroup, Ad, BrandNewContract, Campaign, BusinessChannel

---

## W001: schedule 필드 타입 불일치

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension: create |
| **필드** | `schedule` |
| **Request body 타입** | `object` |
| **Response 타입** | `string` |
| **문제** | 같은 필드가 요청 시 `object`, 응답 시 `string`으로 서로 다른 타입으로 문서화되어 있음 |
| **참고** | list-by-ids 및 get 응답에서도 `string`으로 표기됨 |

---

## W002: enable 필드 — Request에만 존재, Response에 없음

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension: create |
| **필드** | `enable` |
| **문제** | Request body에는 `enable (boolean)` 필드가 있으나 Response 스키마에는 해당 필드가 존재하지 않음 |
| **설명** | Request 파라미터 설명란이 비어 있어 용도 불명확 |

---

## W003: preNccAdExtensionId 필드 설명 없음

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension: create |
| **필드** | `preNccAdExtensionId` |
| **문제** | Request body에 존재하나 설명이 전혀 없음. Response에도 없음. |

---

## W004: statusReason — description 행의 필드명 누락

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension: list (by ids), get, create response |
| **필드** | `statusReason` |
| **문제** | 테이블 행에 필드명(`statusReason`)은 있으나, 행 헤더(row label)가 비어 있음. 접근성 스냅샷 기준 `row [ref=e341]` 처럼 이름 없는 row로 나타남 |

---

## W005: type 필드 — "API 생성 불가 유형" 일부가 전체 enum에도 포함됨

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension 전체 |
| **필드** | `type` |
| **문제** | 문서에서 "API를 이용하여 생성 불가능한 유형"으로 명시된 값들(`SHOPPING_EXTRA`, `CATALOG_EXTRA` 등)이 `type` 필드의 Valid items 목록에도 동시에 포함되어 있음. 생성 불가 여부가 enum 구분 없이 혼재됨. |

---

## W006: Error Response 섹션 없음

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension 모든 operation |
| **문제** | 수집된 3개 endpoint 모두 HTTP 에러 코드(4xx, 5xx) 및 에러 응답 스키마 정보가 문서에 없음 |
| **표기** | 각 raw-md 파일에 "확인불가"로 기록 |

---

## W007: AdExtension update items — Vue.js 템플릿 미렌더링 (type 컬럼)

| 항목 | 내용 |
|------|------|
| **위치** | AdExtension: update items |
| **필드** | request body의 `items[]` 요소 타입 |
| **문제** | 타입 컬럼에 `{{ vm.getType(item, true) }}AdExtensionRequest` 가 그대로 렌더링됨 — Vue.js 템플릿 표현식이 미처리된 상태로 노출 |
| **실제 의도** | `AdExtensionRequest` 타입으로 추정 |

---

## W008: Error Response 섹션 없음 (전체)

| 항목 | 내용 |
|------|------|
| **위치** | 수집된 모든 operation |
| **문제** | HTTP 에러 코드(4xx, 5xx) 및 에러 응답 스키마 정보가 문서 전반에 걸쳐 없음 |
| **표기** | 각 raw-md 파일에 "확인불가"로 기록 |

---

## W009: Campaign trackingUrlCustomParams 타입 불일치

| 항목 | 내용 |
|------|------|
| **위치** | Campaign: create, update (request), Campaign: get, update (response) |
| **필드** | `trackingUrlCustomParams` |
| **Request body 타입** | `object` |
| **Response 타입** | `string` |
| **문제** | 같은 필드가 요청 시 `object`, 응답 시 `string`으로 서로 다른 타입으로 문서화되어 있음 |

---

## W010: BusinessChannel create — nidAut/nidSes/passNaTokenToSa 타입 미렌더링

| 항목 | 내용 |
|------|------|
| **위치** | BusinessChannel: create |
| **필드** | `nidAut`, `nidSes`, `passNaTokenToSa` |
| **문제** | 타입 컬럼에 `{{ vm.getType(item, true) }}` 가 그대로 렌더링됨 — Vue.js 템플릿 표현식이 미처리된 상태로 노출 |
| **표기** | 각 필드 타입을 "확인불가"로 기록 |

---

## W011: AdKeyword attr 타입 불일치

| 항목 | 내용 |
|------|------|
| **위치** | AdKeyword: update, update-items |
| **필드** | `attr` |
| **Request body 타입** | `object` |
| **Response 타입** | `string` |
| **문제** | 같은 필드가 요청 시 `object`, 응답 시 `string`으로 서로 다른 타입으로 문서화되어 있음 |

---

## W012: InspectHistory inquiry — Request body 필드명 불명확

| 항목 | 내용 |
|------|------|
| **위치** | InspectHistory: Inspection history inquiry |
| **필드** | Request body 루트 파라미터 |
| **문제** | Request body 파라미터 이름이 `[]` (익명 배열)로만 표기되어 있고 별도 필드명이 없음. 단순 string 배열을 직접 body로 전달하는 구조로 추정 |

---

## W013: InspectHistory response — id 필드 설명 없음

| 항목 | 내용 |
|------|------|
| **위치** | InspectHistory: 두 operation 모두 |
| **필드** | `id` |
| **문제** | Response의 `id` 필드에 설명(Description)이 없음. 어떤 엔티티의 ID인지 불명확 |

---

## W014: StatReport — delete 와 delete(by id) 사이드바 레이블 중복

| 항목 | 내용 |
|------|------|
| **위치** | StatReport group |
| **문제** | 사이드바에 "delete" 레이블이 두 번 나타남. 하나는 DELETE /stat-reports (전체 삭제), 다른 하나는 DELETE /stat-reports/{reportJobId} (단건 삭제). 두 번째 항목도 "delete"로 표기되어 있어 혼동 가능. endpoints.csv에서는 "delete"와 "delete (by id)"로 구분하여 기록 |

---

## W015: Estimate NPC — 문서상 operation 목록에 get (median bid) - NPC 없음

| 항목 | 내용 |
|------|------|
| **위치** | Estimate group (NPC) |
| **문제** | NPLA에는 없는 `average-position-bid`, `exposure-minimum-bid`, `performance` 3종이 NPC에 있으나, 일반 estimate에 있는 `median-bid` 에 해당하는 NPC 버전이 존재하지 않음. 의도적 누락인지 미구현인지 불명확 |

---

_마지막 업데이트: 2026-05-18 (전체 수집 완료 — 15개 그룹, 115개 operation)_
