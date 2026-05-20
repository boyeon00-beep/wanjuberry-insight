# 네이버 검색광고 API 품질 리포트

> 생성일: 2026-05-19 (보정: 2026-05-19, safe 기준 통일: 2026-05-19)  
> 입력 소스: action-map.json (source of truth), normalized-api.json, endpoints.csv, warnings.md  
> 총 operation 수: 119 (실제 API endpoint 117 + spec 문서 2)  
> **위험도 통계는 action-map.json 기준**

---

## 1. 전체 통계

### 1-1. 전체 operation 수

| 구분 | 수 |
|------|-----|
| 전체 operation | 119 |
| 실제 API endpoint | 117 |
| spec 참조 문서 | 2 |

### 1-2. Group별 operation 수

| Group | 수 |
|-------|-----|
| Ad | 7 |
| AdAccounts | 2 |
| AdExtension | 8 |
| AdKeyword | 9 |
| Adgroup | 12 |
| Bizmoney | 4 |
| BrandNewContract | 2 |
| BusinessChannel | 10 |
| Campaign | 8 |
| Criterion | 4 |
| Estimate | 10 |
| InspectHistory | 2 |
| IpExclusion | 5 |
| Label | 2 |
| LabelRef | 1 |
| ManagedKeyword | 1 |
| ManagerAccounts | 2 |
| MasterReport | 5 (+1 spec) |
| ProductGroup | 1 |
| RelKwdStat | 1 |
| SharedBudget | 8 |
| Stat | 3 |
| StatReport | 5 (+1 spec) |
| Target | 3 |
| TimeContract | 2 |
| **합계** | **119** |

### 1-3. Method별 operation 수

| Method | 수 | 비고 |
|--------|-----|------|
| GET | 57 | 47.9% |
| POST | 22 | 18.5% |
| PUT | 21 | 17.6% |
| DELETE | 17 | 14.3% |
| (없음) | 2 | spec 문서 |
| **합계** | **119** | |

### 1-4. response.type별 operation 수

| response.type | 수 |
|---------------|-----|
| object | 54 |
| array | 42 |
| unknown | 23 |
| **합계** | **119** |

> unknown 23개: spec 2 + DELETE 14 + 기타 7

### 1-5. action_type별 operation 수 (action-map.json 기준)

| action_type | 수 | 주요 구성 |
|-------------|-----|---------|
| read | 44 | GET 조회 (LOW 40, MEDIUM 4) |
| report | 26 | 통계/추정/이력 조회 (LOW 13, MEDIUM 13) |
| update | 21 | PUT 수정 (CRITICAL 14, HIGH 7) |
| delete | 17 | DELETE (전체 CRITICAL) |
| create | 9 | POST 생성 (전체 HIGH) |
| spec | 2 | 참조 문서 (LOW) |
| **합계** | **119** | |

### 1-6. risk_level별 operation 수 (action-map.json 기준)

| risk_level | 수 | safe=true | requires_review=true |
|------------|-----|----------|---------------------|
| LOW | 55 | 55 | 0 |
| MEDIUM | 17 | **17** | 0 |
| HIGH | 16 | 0 | 16 |
| CRITICAL | 31 | 0 | 31 |
| **합계** | **119** | **72** | **47** |

> MEDIUM safe=true 17개: report 13 + read 4 (budget 경로 포함 GET — 데이터 변경 없음, 민감 데이터 조회 가능)  
> safe_for_direct_execution 기준 = **실행 자체의 부작용(데이터 변경) 여부**

### 1-7. warning 포함 operation 수

| 구분 | 수 |
|------|-----|
| W008 포함 (전체: error response 없음) | 119 |
| W008 외 추가 warning 포함 | 28 |
| W008만 포함 (추가 warning 없음) | 91 |

### 1-8. error_response 확인불가 수

| 구분 | 수 |
|------|-----|
| error_response = 확인불가 | 119 |
| error_response 확인 가능 | 0 |

> W008: HTTP 4xx/5xx 에러 응답 스키마가 API 문서 전반에 걸쳐 미수록

---

## 2. Response 품질 분석

### 2-1. response.fields 없는 operation 목록 (23개)

spec 2 + DELETE 14 + 기타 7 (response 스키마 문서 없음)

| operation_id | method | 사유 |
|---|---|---|
| MasterReport-spec | (none) | spec 문서 |
| StatReport-spec | (none) | spec 문서 |
| Ad-delete | DELETE | DELETE 응답 없음 |
| AdExtension-delete | DELETE | DELETE 응답 없음 |
| AdKeyword-delete | DELETE | DELETE 응답 없음 |
| AdKeyword-delete-items | DELETE | DELETE 응답 없음 |
| Adgroup-delete | DELETE | DELETE 응답 없음 |
| Adgroup-delete-negative-search-terms | DELETE | DELETE 응답 없음 |
| BusinessChannel-delete | DELETE | DELETE 응답 없음 |
| BusinessChannel-delete-items | DELETE | DELETE 응답 없음 |
| Campaign-delete | DELETE | DELETE 응답 없음 |
| Campaign-delete-items | DELETE | DELETE 응답 없음 |
| MasterReport-delete | DELETE | DELETE 응답 없음 |
| MasterReport-delete-all | DELETE | DELETE 응답 없음 |
| SharedBudget-delete | DELETE | DELETE 응답 없음 |
| StatReport-delete | DELETE | DELETE 응답 없음 |
| StatReport-delete-all | DELETE | DELETE 응답 없음 |
| Adgroup-create-negative-search-terms | POST | 응답 스키마 문서 없음 |
| IpExclusion-delete-by-ids | DELETE | DELETE 응답 없음 |
| SharedBudget-exclude-adgroups | PUT | 응답 스키마 문서 없음 |
| SharedBudget-exclude-campaigns | PUT | 응답 스키마 문서 없음 |
| Criterion-update-bidWeight | PUT | 응답 fields 미명세 |
| Criterion-update-Criterion | PUT | 응답 fields 미명세 |

### 2-2. response.type = unknown 목록 (23개)

MasterReport-spec, StatReport-spec, Ad-delete, AdExtension-delete, AdKeyword-delete, AdKeyword-delete-items, Adgroup-create-negative-search-terms, Adgroup-delete, Adgroup-delete-negative-search-terms, BusinessChannel-delete, BusinessChannel-delete-items, Campaign-delete, Campaign-delete-items, IpExclusion-delete-by-ids, MasterReport-delete, MasterReport-delete-all, SharedBudget-delete, SharedBudget-exclude-adgroups, SharedBudget-exclude-campaigns, StatReport-delete, StatReport-delete-all, Criterion-update-bidWeight *(부분)*, Criterion-update-Criterion *(부분)*

### 2-3. 참조 병합(response_source_file) 사용 operation 수

| 구분 | 수 |
|------|-----|
| response fields 병합 성공 | 43 |
| 텍스트 참조 수동 패치 | 3 |
| **병합/패치 총계** | **46** |

---

## 3. Warning 분석

### 3-1. Warning 코드 전체 현황

| 코드 | 종류 | 영향 operation 수 |
|------|------|-----------------|
| W001 | 타입 불일치 (schedule: object→string) | 1 |
| W002 | request/response 구조 불일치 (enable 필드 응답 누락) | 1 |
| W003 | 설명 없음 (preNccAdExtensionId) | 1 |
| W004 | row label 누락 (statusReason 필드명) | 3 |
| W005 | enum 참조 혼재 (API 생성불가 유형 포함) | 8 |
| W007 | 템플릿 미렌더링 (Vue.js — update items) | 1 |
| W008 | error response 스키마 없음 (전체) | 119 |
| W009 | 타입 불일치 (trackingUrlCustomParams: object→string) | 3 |
| W010 | 템플릿 미렌더링 (Vue.js — BusinessChannel) | 1 |
| W011 | 타입 불일치 (attr: object→string) | 2 |
| W012 | request 구조 불명확 (익명 배열 body) | 1 |
| W013 | 설명 없음 (id 필드) | 2 |
| W014 | 사이드바 레이블 중복 (delete 이름 중복) | 2 |
| W015 | 문서 누락 (Estimate NPC median-bid 없음) | 10 |

### 3-2. Warning 종류별 집계

| 경고 유형 | 해당 코드 | 영향 operation 수 |
|-----------|-----------|-----------------|
| **타입 불일치** | W001, W009, W011 | 6 |
| **enum 참조 문제** | W004, W005 | 8 |
| **템플릿 미렌더링** | W007, W010 | 2 |
| **response 불명확/누락** | W002, W008 | 119 (W008 전체 포함) |
| **설명 없음** | W003, W013 | 3 |
| **request/response 구조 불일치** | W012 | 1 |
| **문서 레이블/구조 문제** | W014, W015 | 12 |

---

## 4. 위험 Endpoint 분류

> **기준: action-map.json (source of truth)**  
> risk_level 산정 방식: method(GET=LOW, POST=MEDIUM, PUT=HIGH, DELETE=CRITICAL) + 위험 조건 1단계 상승  
> 위험 조건: budget, bid, status, userLock, bulk(-items/-all), pause, suspend, exposure 관련 필드/operation

### 4-0. 위험도 요약 통계

| risk_level | 수 | safe_for_direct_execution=true | requires_manual_review=true |
|---|---|---|---|
| LOW | 55 | 55 | 0 |
| MEDIUM | 17 | **17** | 0 |
| HIGH | 16 | 0 | 16 |
| CRITICAL | 31 | 0 | 31 |
| **합계** | **119** | **72** | **47** |

### 4-1. CRITICAL (31개) — 직접 실행 금지

#### DELETE operations (17개)

| operation_id | path | 비고 |
|---|---|---|
| Ad-delete | /ncc/ads/{adId} | 광고 삭제 |
| AdExtension-delete | /ncc/ad-extensions/{adExtensionId} | 확장 소재 삭제 + W005 |
| AdKeyword-delete | /ncc/keywords/{nccKeywordId} | 키워드 삭제 |
| AdKeyword-delete-items | /ncc/keywords{?ids} | 키워드 대량 삭제 |
| Adgroup-delete | /ncc/adgroups/{adgroupId} | 광고그룹 삭제 |
| Adgroup-delete-negative-search-terms | /ncc/adgroups/{adgroupId}/restricted-keywords{?ids} | 제한 키워드 삭제 |
| BusinessChannel-delete | /ncc/channels/{businessChannelId} | 비즈채널 삭제 |
| BusinessChannel-delete-items | /ncc/channels{?ids} | 비즈채널 대량 삭제 |
| Campaign-delete | /ncc/campaigns/{campaignId} | 캠페인 삭제 |
| Campaign-delete-items | /ncc/campaigns{?ids} | 캠페인 대량 삭제 |
| IpExclusion-delete | /tool/ip-exclusions/{id} | IP 차단 삭제 |
| IpExclusion-delete-by-ids | /tool/ip-exclusions{?ids} | IP 차단 대량 삭제 |
| MasterReport-delete | /master-reports/{id} | 마스터 리포트 삭제 |
| MasterReport-delete-all | /master-reports | 마스터 리포트 전체 삭제 |
| SharedBudget-delete | /ncc/shared-budgets{?ids} | 공유 예산 삭제 |
| StatReport-delete | /stat-reports | 통계 리포트 삭제 (전체) + W014 |
| StatReport-delete-all | /stat-reports | 통계 리포트 삭제 (전체) + W014 |

#### PUT escalated — 상태/예산/입찰/대량 변경 (14개)

| operation_id | path | 상승 이유 |
|---|---|---|
| Ad-copy | /ncc/ads{?ids,targetAdgroupId,userLock} | userLock in path |
| Ad-update | /ncc/ads/{adId}{?fields} | userLock in body |
| AdExtension-update-items | /ncc/ad-extensions{?fields} | bulk(-items) |
| AdKeyword-update | /ncc/keywords/{nccKeywordId}{?fields} | bid(AdKeyword) + userLock in body |
| AdKeyword-update-items | /ncc/keywords{?fields} | bulk(-items) |
| Adgroup-update | /ncc/adgroups/{adgroupId} | budget(Adgroup) + userLock in body |
| Adgroup-update-by-fields | /ncc/adgroups/{adgroupId}{?fields} | budget(Adgroup) + userLock in body |
| BusinessChannel-request-inspect | /ncc/channels/{businessChannelId}/inspect | status in body |
| Campaign-update | /ncc/campaigns/{campaignId}{?fields} | campaign budget + userLock in body |
| Criterion-update-bidWeight | /ncc/criterion/{ownerId}/bidWeight{?codes,bidWeight} | bid (bidWeight 직접 수정) |
| SharedBudget-exclude-adgroups | /ncc/shared-budgets/adgroups{?ids} | budget(SharedBudget) |
| SharedBudget-exclude-campaigns | /ncc/shared-budgets/campaigns{?ids} | budget(SharedBudget) |
| SharedBudget-update | /ncc/shared-budgets/{sharedBudgetId} | budget(SharedBudget) |
| SharedBudget-update-budget | /ncc/shared-budgets{?fields} | budget(SharedBudget) |

### 4-2. HIGH (16개) — 수동 검토 필요

#### POST create — 광고 객체/예산/노출 관련 생성 (9개)

| operation_id | path | 비고 |
|---|---|---|
| Ad-create | /ncc/ads | userLock in body |
| AdExtension-create | /ncc/ad-extensions | W001+W002+W003+W004+W005, userLock 필수 |
| AdKeyword-create | /ncc/keywords{?nccAdgroupId} | 광고 키워드 생성 |
| Adgroup-create | /ncc/adgroups | userLock in body |
| Adgroup-create-negative-search-terms | /ncc/adgroups/{adgroupId}/restricted-keywords | 광고 타겟팅 영향 |
| BusinessChannel-create | /ncc/channels | W010, 비즈채널 생성 |
| Campaign-create | /ncc/campaigns | campaign budget, userLock in body, W009 |
| IpExclusion-create | /tool/ip-exclusions | 노출 제한 생성 |
| SharedBudget-create | /ncc/shared-budgets | 공유 예산 생성 |

#### PUT single — 경미한 단일 수정 (7개)

| operation_id | path | 비고 |
|---|---|---|
| AdExtension-update | /ncc/ad-extensions/{adExtensionId}{?fields} | W005 |
| BusinessChannel-update | /ncc/channels/{businessChannelId}{?fields} | |
| Criterion-update-Criterion | /ncc/criterion/{ownerId}/{type} | 타겟팅 기준 변경 |
| IpExclusion-update | /tool/ip-exclusions | |
| Label-update | /ncc/labels | |
| LabelRef-update | /ncc/label-refs | |
| Target-update | /ncc/targets/{targetId} | |

### 4-3. MEDIUM (17개) — 제한적 자동 실행 또는 입력값 검토 권장

> safe_for_direct_execution 기준 = 실행 자체의 부작용(데이터 변경) 여부.  
> 데이터를 변경하지 않는 MEDIUM read/report는 safe=**true**. 민감 데이터 조회 가능성이 있는 경우 notes에 명시.

| operation_id | method | action_type | safe | 비고 |
|---|---|---|---|---|
| Adgroup-list-by-shared-budget-id | GET | read | **true** | 민감 데이터 조회 가능 (budget 경로) |
| Campaign-list-by-shared-budget-id | GET | read | **true** | 민감 데이터 조회 가능 (budget 경로) |
| Estimate-get-average-position-bid | POST | report | **true** | 읽기 전용 추정 |
| Estimate-get-average-position-bid-npc | POST | report | **true** | 읽기 전용 + W015 |
| Estimate-get-average-position-bid-npla | POST | report | **true** | 읽기 전용 + W015 |
| Estimate-get-exposure-minimum-bid | POST | report | **true** | 읽기 전용 추정 |
| Estimate-get-exposure-minimum-bid-npc | POST | report | **true** | 읽기 전용 + W015 |
| Estimate-get-exposure-minimum-bid-npla | POST | report | **true** | 읽기 전용 + W015 |
| Estimate-get-median-bid | POST | report | **true** | 읽기 전용 + W015 |
| Estimate-get-performance | POST | report | **true** | 읽기 전용 추정 |
| Estimate-get-performance-bulk | POST | report | **true** | 읽기 전용 추정 |
| Estimate-get-performance-npc | POST | report | **true** | 읽기 전용 + W015 |
| InspectHistory-inquiry | POST | report | **true** | 심사 이력 조회 (읽기 전용) |
| MasterReport-create | POST | report | **true** | 리포트 작업 생성 |
| SharedBudget-get | GET | read | **true** | 민감 데이터 조회 가능 (예산 목록) |
| SharedBudget-get-by-id | GET | read | **true** | 민감 데이터 조회 가능 (예산 상세) |
| StatReport-create | POST | report | **true** | 통계 리포트 작업 생성 |

> safe=true: 전체 17개 (MEDIUM 전원)  
> 민감 데이터 조회 가능 (safe=true이나 주의 필요): SharedBudget-get, SharedBudget-get-by-id, Campaign-list-by-shared-budget-id, Adgroup-list-by-shared-budget-id

### 4-4. LOW (55개) — 자동 실행 가능

spec 2개, read 40개, report 13개. 전체 safe_for_direct_execution=true.

**spec (2)**:  
MasterReport-spec, StatReport-spec

**report (13)**:  
Bizmoney-get, Bizmoney-get-charge, Bizmoney-get-exhaust, Bizmoney-get-period,  
InspectHistory-single-inquiry, MasterReport-get, MasterReport-list,  
RelKwdStat-list, Stat-get-by-id, Stat-get-by-ids, Stat-get-by-stattype,  
StatReport-get, StatReport-list

**read (40)**:  
Ad-get, Ad-list, Ad-list-by-adgroup-id,  
AdAccounts-list, AdAccounts-retrieve-member-list,  
AdExtension-get, AdExtension-list-by-ids, AdExtension-list-by-label-id, AdExtension-list-by-owner-id,  
AdKeyword-get, AdKeyword-list, AdKeyword-list-by-adgroup-id, AdKeyword-list-by-label-id,  
Adgroup-get, Adgroup-list-by-campaign-id, Adgroup-list-by-ids, Adgroup-list-by-label-id, Adgroup-list-negative-search-terms,  
BrandNewContract-list, BrandNewContract-list-by-adgroup-id,  
BusinessChannel-get, BusinessChannel-list, BusinessChannel-list-by-channelTp, BusinessChannel-list-by-ids, BusinessChannel-list-purchasable-place-channels,  
Campaign-get, Campaign-list-by-customer-id, Campaign-list-by-ids,  
Criterion-get-dictionary-code, Criterion-list-by-id,  
IpExclusion-get, Label-list, ManagedKeyword-list-by-keywords,  
ManagerAccounts-list, ManagerAccounts-retrieve-child-ad-account-list,  
ProductGroup-get, Target-list-by-owner-id, Target-list-by-owner-id-list,  
TimeContract-list, TimeContract-list-by-adgroup-id

---

## 5. 실제 API 테스트 권장 Endpoint

문서 구조가 명확하고 부작용이 없는 LOW 조회 endpoint.

| operation_id | method | path | 권장 이유 |
|---|---|---|---|
| Ad-get | GET | /ncc/ads/{adId} | response 스키마 완전, 단건 조회 |
| AdKeyword-get | GET | /ncc/keywords/{nccKeywordId} | response 스키마 완전 |
| Adgroup-get | GET | /ncc/adgroups/{adgroupId} | response 스키마 완전 (37 fields) |
| Campaign-list-by-ids | GET | /ncc/campaigns{?ids} | 단순 조회, 부작용 없음 |
| Stat-get-by-id | GET | /stats{?id,...} | 통계 조회, 부작용 없음 |
| Stat-get-by-ids | GET | /stats{?ids,...} | 통계 조회, 부작용 없음 |
| RelKwdStat-list | GET | /keywordstool | 키워드 도구, 부작용 없음 |
| SharedBudget-get-by-id | GET | /ncc/shared-budgets/{sharedBudgetId} | 예산 조회, 부작용 없음 |
| Bizmoney-get | GET | /billing/bizmoney | 잔액 조회, 부작용 없음 |
| ManagerAccounts-list | GET | /manager-accounts | 계정 조회, 부작용 없음 |

---

## 6. 문서만으로 구현 가능성이 높은 Endpoint

response 스키마 완전 + W008 외 warning 없음 + 파라미터 명세 명확.

| operation_id | method | path | 근거 |
|---|---|---|---|
| Ad-get | GET | /ncc/ads/{adId} | fields 완전, enum 명세 있음 |
| Ad-list | GET | /ncc/ads{?ids} | fields 완전 (Ad-get 병합) |
| AdKeyword-get | GET | /ncc/keywords/{nccKeywordId} | fields 완전 |
| AdKeyword-list | GET | /ncc/keywords{?ids} | fields 완전 |
| AdKeyword-list-by-adgroup-id | GET | /ncc/keywords{?nccAdgroupId,...} | fields 완전 |
| Adgroup-get | GET | /ncc/adgroups/{adgroupId} | fields 완전 (37 fields) |
| Adgroup-list-by-campaign-id | GET | /ncc/adgroups{?nccCampaignId,...} | fields 완전 |
| IpExclusion-get | GET | /tool/ip-exclusions | fields 완전 |
| Label-list | GET | /ncc/labels | fields 완전 (Label-list 병합) |
| MasterReport-list | GET | /master-reports | fields 완전, enum 있음 |
| SharedBudget-get-by-id | GET | /ncc/shared-budgets/{sharedBudgetId} | fields 완전 |
| Stat-get-by-id | GET | /stats{?id,...} | 파라미터 명세 명확 |
| Stat-get-by-ids | GET | /stats{?ids,...} | 파라미터 명세 명확 |
| StatReport-list | GET | /stat-reports | fields 완전, enum 있음 |
| AdKeyword-create | POST | /ncc/keywords{?nccAdgroupId} | 파라미터 명세 명확 |
| AdExtension-list-by-ids | GET | /ncc/ad-extensions{?ids} | fields 완전 (W005 주의) |

---

## 7. 문서 품질이 낮은 Endpoint 목록

warning 다수 또는 response 불명확 또는 구조 미렌더링 포함.

| operation_id | method | 문제 코드 | 문제 설명 |
|---|---|---|---|
| AdExtension-create | POST | W001,W002,W003,W004,W005 | 5개 warning — type enum 혼재, schedule 타입 불일치, enable 필드 응답 누락, preNccAdExtensionId 설명 없음 |
| AdExtension-update-items | PUT | W005,W007 | Vue.js 템플릿 미렌더링으로 items 타입 확인불가 |
| BusinessChannel-create | POST | W010 | nidAut/nidSes/passNaTokenToSa 타입 미렌더링 |
| Campaign-create | POST | W009 | trackingUrlCustomParams Request:object / Response:string 타입 불일치 |
| Campaign-update | PUT | W009 | 동일 타입 불일치 |
| AdKeyword-update | PUT | W011 | attr Request:object / Response:string 타입 불일치 |
| AdKeyword-update-items | PUT | W011 | 동일 타입 불일치 |
| InspectHistory-inquiry | POST | W012,W013 | request body 필드명 불명확(익명 배열), id 필드 설명 없음 |
| StatReport-delete-all | DELETE | W014 | 사이드바 레이블 중복으로 단건/전체 삭제 혼동 가능 |
| Adgroup-create-negative-search-terms | POST | — | response.type=unknown, 응답 스키마 없음 |
| SharedBudget-exclude-adgroups | PUT | — | response.type=unknown, 응답 스키마 없음 |
| SharedBudget-exclude-campaigns | PUT | — | response.type=unknown, 응답 스키마 없음 |
| Criterion-update-bidWeight | PUT | — | response fields 미명세 |
| Criterion-update-Criterion | PUT | — | response fields 미명세 |

---

_생성: 2026-05-19 | 보정: 2026-05-19 | 기준: action-map.json (119 operations)_
