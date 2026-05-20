# Approval Policy — 네이버 검색광고 API 실행 정책

> 생성일: 2026-05-19 (보정: 2026-05-19, safe 기준 통일: 2026-05-19)  
> 기준: action-map.json (source of truth)  
> 적용 범위: 이 문서는 독립 작업공간(API 문서 메타데이터 구축)의 실행 정책 참조용이다.

---

## 0. 정책 요약 매트릭스 (action-map.json 기준)

| risk_level | action_type | safe_for_direct_execution | requires_manual_review | 수 | 정책 |
|---|---|---|---|---|---|
| LOW | read / report / spec | **true** | false | 55 | 자동 실행 가능 |
| MEDIUM | report (읽기 전용) | **true** | false | 13 | 제한적 자동 실행 |
| MEDIUM | read (budget 경로 포함) | **true** ※ | false | 4 | 제한적 자동 실행 (민감 데이터) |
| HIGH | create / update | false | **true** | 16 | 수동 검토 필요 |
| CRITICAL | update / delete | false | **true** | 31 | 직접 실행 금지 |
| **합계** | | **72 safe=true** | **47 review=true** | **119** | |

> ※ MEDIUM + read: `safe_for_direct_execution=true`이나 `notes="민감 데이터 조회 가능"` 기재.  
> safe의 의미 = **실행 자체의 부작용 여부** (데이터 변경 없음). 민감 데이터 노출 위험은 별도 접근 제어로 관리.

---

## 1. 자동 실행 가능한 Endpoint 유형

### 조건

- `risk_level = LOW`
- `action_type ∈ { read, report, spec }`
- `safe_for_direct_execution = true`
- W008 외 추가 warning 없음 (단, 해당 operation의 W004/W005 등은 응답 파싱 시 주의)

### 해당 유형 (55개)

| 유형 | action_type | 수 | 예시 |
|------|-------------|-----|------|
| 단순 조회 (GET) | read | 40 | Ad-get, Adgroup-get, Campaign-list-by-ids |
| 통계/리포트 조회 (GET) | report | 13 | Stat-get-by-id, Bizmoney-get, StatReport-list, RelKwdStat-list |
| spec 참조 문서 | spec | 2 | MasterReport-spec, StatReport-spec |

### 주의 사항

- 비정상적 요청 빈도 발생 시 알림 권장
- AdExtension 계열 GET (W004/W005): 응답의 `type`, `statusReason` 필드 파싱 시 주의

---

## 2. 제한적 자동 실행 가능한 Endpoint 유형

> **safe_for_direct_execution의 의미**: 실행 자체의 부작용(데이터 변경/삭제) 여부.  
> risk_level=MEDIUM이라도 데이터를 변경하지 않는 read/report endpoint는 `safe=true`.  
> 단, 민감 데이터(예산 구조, 공유 예산 연결 정보 등) 조회 가능성이 있으면 `notes="민감 데이터 조회 가능"` 기재.

### 조건

- `risk_level = MEDIUM`
- `action_type ∈ { read, report }`
- `safe_for_direct_execution = true`
- 데이터 변경 없음

### 해당 유형 (17개 = report 13 + read 4)

#### 2-1. MEDIUM + report — 읽기 전용 추정/리포트 (13개)

| operation_id | method | 비고 |
|---|---|---|
| Estimate-get-average-position-bid | POST | 입찰가 추정 — 읽기 전용 |
| Estimate-get-average-position-bid-npc | POST | W015 |
| Estimate-get-average-position-bid-npla | POST | W015 |
| Estimate-get-exposure-minimum-bid | POST | 최소 입찰가 추정 |
| Estimate-get-exposure-minimum-bid-npc | POST | W015 |
| Estimate-get-exposure-minimum-bid-npla | POST | W015 |
| Estimate-get-median-bid | POST | W015 |
| Estimate-get-performance | POST | 성과 추정 |
| Estimate-get-performance-bulk | POST | |
| Estimate-get-performance-npc | POST | W015 |
| InspectHistory-inquiry | POST | 심사 이력 검색 — 읽기 전용 |
| MasterReport-create | POST | 리포트 작업 생성 (광고 데이터 미변경) |
| StatReport-create | POST | 통계 리포트 작업 생성 (광고 데이터 미변경) |

#### 2-2. MEDIUM + read — 민감 데이터 포함 GET (4개)

데이터 변경 없음. 단, 예산 구조/공유 예산 연결 정보 등 민감 데이터 조회 가능.  
`notes = "민감 데이터 조회 가능"` (action-map.json 기재)

| operation_id | method | path | 민감 데이터 유형 |
|---|---|---|---|
| SharedBudget-get | GET | /ncc/shared-budgets | 공유 예산 목록 |
| SharedBudget-get-by-id | GET | /ncc/shared-budgets/{sharedBudgetId} | 공유 예산 상세 |
| Campaign-list-by-shared-budget-id | GET | /ncc/campaigns/shared-budgets/{sharedBudgetId} | 예산 연결 캠페인 목록 |
| Adgroup-list-by-shared-budget-id | GET | /ncc/adgroups/shared-budgets/{sharedBudgetId} | 예산 연결 광고그룹 목록 |

### 요구 사항 (MEDIUM 공통)

- rate limit 적용 권장 (특히 Estimate 계열 bulk 호출 시)
- 호출 로그 기록
- 입력 파라미터 타입 검증 (W015: Estimate NPC median-bid 문서 없음 주의)
- InspectHistory-inquiry (W012): request body를 익명 배열 형식으로 전송
- MEDIUM + read (민감): 응답에 예산 금액/구조 포함 — 접근 권한 사전 확인 권장

---

## 3. 수동 검토가 필요한 Endpoint 유형

### 조건

다음 중 하나 이상 해당:
- `risk_level = MEDIUM` + `action_type = create` (광고 데이터 변경)
- `risk_level = HIGH` (모든 HIGH)

### 3-1. MEDIUM + create — 수동 검토 권장

> action_type=create이지만 risk_level=MEDIUM인 경우.  
> (현재 이 조합에 해당하는 operation 없음 — 모든 create는 HIGH로 상향됨)

### 3-2. HIGH — 수동 검토 필수 (16개)

`requires_manual_review = true`, `safe_for_direct_execution = false`

#### POST create — 광고 객체/예산/노출 관련 (9개)

| operation_id | path | 주요 위험 필드 |
|---|---|---|
| Ad-create | /ncc/ads | userLock |
| AdExtension-create | /ncc/ad-extensions | userLock, enable (W001-W005) |
| AdKeyword-create | /ncc/keywords{?nccAdgroupId} | 광고 키워드 생성 |
| Adgroup-create | /ncc/adgroups | bidAmt, userLock |
| Adgroup-create-negative-search-terms | /ncc/adgroups/{adgroupId}/restricted-keywords | 타겟팅 영향 |
| BusinessChannel-create | /ncc/channels | W010 (타입 확인불가 필드) |
| Campaign-create | /ncc/campaigns | userLock, W009 |
| IpExclusion-create | /tool/ip-exclusions | 노출 제한 |
| SharedBudget-create | /ncc/shared-budgets | 예산 생성 |

#### PUT — 단일 수정 (7개)

| operation_id | path | 주요 위험 필드 |
|---|---|---|
| AdExtension-update | /ncc/ad-extensions/{adExtensionId}{?fields} | enable (W005) |
| BusinessChannel-update | /ncc/channels/{businessChannelId}{?fields} | |
| Criterion-update-Criterion | /ncc/criterion/{ownerId}/{type} | 타겟팅 기준 |
| IpExclusion-update | /tool/ip-exclusions | |
| Label-update | /ncc/labels | |
| LabelRef-update | /ncc/label-refs | |
| Target-update | /ncc/targets/{targetId} | |

### 검토 항목 (HIGH 공통)

1. `required_inputs` 목록의 모든 필드 제공 확인
2. `dangerous_fields` 값의 의도적 설정 여부 확인
3. 가능한 경우 테스트 계정으로 선행 검증
4. 실행 결과 즉시 GET 조회로 검증
5. 롤백 계획 사전 수립

---

## 4. 직접 실행 금지 Endpoint 유형

### 조건

- `risk_level = CRITICAL`
- `safe_for_direct_execution = false`
- `requires_manual_review = true`

총 **31개**. 자동화 스크립트/AI agent 직접 호출 금지.

### 4-1. DELETE (17개) — 삭제 금지

| 유형 | 해당 수 | 대표 operation |
|------|---------|--------------|
| 단건 삭제 | 13 | Ad-delete, AdKeyword-delete, Campaign-delete |
| 대량 삭제 (-items) | 3 | Campaign-delete-items, BusinessChannel-delete-items, AdKeyword-delete-items |
| 전체 삭제 (-all) | 1 | MasterReport-delete-all |

### 4-2. PUT escalated (14개) — 위험 변경 금지

| 유형 | 해당 수 | 대표 operation |
|------|---------|--------------|
| 예산 수정 (SharedBudget) | 4 | SharedBudget-update, SharedBudget-update-budget, SharedBudget-exclude-* |
| 입찰가 수정 | 3 | Criterion-update-bidWeight, AdKeyword-update, AdKeyword-update-items |
| 상태/userLock 변경 | 4 | Ad-copy, Ad-update, Campaign-update, BusinessChannel-request-inspect |
| 대량 수정 (-items) | 2 | AdExtension-update-items, AdKeyword-update-items |
| 광고그룹 예산 수정 | 2 | Adgroup-update, Adgroup-update-by-fields |

### 요구 사항 (CRITICAL 공통)

```
1. 인간 검토자의 명시적 승인 필수
2. 실행 전 영향 범위 산정 (삭제 대상 수, 예산 변경량, 노출 영향 등)
3. 테스트 환경 선행 검증 완료 후 운영 환경 실행
4. 삭제 operation: 복구 불가 → 별도 데이터 백업 확인 필수
5. bulk/all 계열: 단건 테스트 후 전체 적용
6. 예산/입찰가 변경: 변경 전/후 수치 명시적 확인
7. status/userLock 변경: 광고 노출 즉시 영향 → 비업무 시간 실행 검토
```

---

## 5. 실행 전 체크 항목 (전체 공통)

| 항목 | 설명 |
|------|------|
| **에러 응답 처리** | W008 (전체): error response 스키마 문서 없음 — 4xx/5xx 처리 로직 사전 구현 필수 |
| **인증 헤더** | X-API-KEY, X-Customer 등 유효성 확인 |
| **required_inputs** | action-map.json required_inputs 필드 전체 제공 |
| **dangerous_fields** | action-map.json dangerous_fields 의도 확인 (status, userLock, bidAmt, budget 등) |
| **경로 파라미터 치환** | `/ncc/ads/{adId}` 형식에서 실제 ID로 치환 확인 |
| **URI template 주의** | `{?ids,fields,...}` 형식 — 쿼리스트링 인코딩 방식 확인 |
| **response.type=unknown** | 응답 파싱 전 null 체크 필요 |

---

## 6. Warning 존재 시 검토 규칙

action-map.json의 `warnings` 배열이 비어있지 않으면 아래 규칙 적용.

| Warning | 적용 규칙 |
|---------|----------|
| **W001** | AdExtension `schedule`: request=object, response=string — 별도 역직렬화 로직 구현 |
| **W002** | AdExtension-create response에 `enable` 필드 없음 — 응답 파싱 시 해당 필드 접근 금지 |
| **W003** | `preNccAdExtensionId` 용도 확인불가 — 기본값 null로만 사용 |
| **W004** | `statusReason` row label 누락 — key 이름 직접 명세 후 파싱 |
| **W005** | AdExtension `type` enum: API 생성 불가 유형 포함 — create 시 허용 21종만 사용 |
| **W007** | AdExtension-update-items items 타입 확인불가 — 구현 전 raw-md 직접 확인 필수 |
| **W009** | Campaign `trackingUrlCustomParams`: request=object, response=string — 별도 처리 필요 |
| **W010** | BusinessChannel-create `nidAut`/`nidSes`/`passNaTokenToSa` 타입 확인불가 — 구현 보류 또는 raw-md 직접 확인 |
| **W011** | AdKeyword `attr`: request=object, response=string — W009와 동일 패턴 |
| **W012** | InspectHistory-inquiry request body 익명 배열 `[]` 형식으로 전송 |
| **W013** | InspectHistory response `id` 필드 용도 확인불가 — 주석 처리 권장 |
| **W014** | StatReport-delete vs StatReport-delete-all 혼동 주의 — path로 반드시 구분 |
| **W015** | Estimate NPC `median-bid` 문서 없음 — 해당 기능 구현 불가 또는 미지원으로 처리 |

---

_생성: 2026-05-19 | 보정: 2026-05-19 | 기준: action-map.json (119 operations)_
