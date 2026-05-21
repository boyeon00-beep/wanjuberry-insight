# 완주베리 AI 운영 인사이트 시스템 — CLAUDE.md

> 이 파일은 Claude Code와 채팅 Claude가 공유하는 프로젝트 컨텍스트다.
> 새 채팅 시작 시 이 파일을 첨부하면 맥락이 유지된다.
> 결정사항이 바뀌면 decision-log.md를 먼저 수정하고 이 파일에 반영한다.

---

## 📁 파일 지도

| 파일 | 역할 | 언제 읽나 |
|---|---|---|
| `CLAUDE.md` | 핵심 철학 + 구조 요약 + 파일 지도 | 항상 |
| `PRD.md` | 기능 명세 (에이전트 상세, 인터페이스, 대시보드) | 에이전트 구현 시 |
| `ARCHITECTURE.md` | 기술 스택, 폴더 구조, 데이터 흐름 | 구현 시작 시 |
| `decision-log.md` | 결정 이력 전체 | 맥락 확인 필요 시 |
| `backend/kb/naver-commerce/commerce-llm.txt` | 네이버 커머스 API 전체 엔드포인트 목록 (LLM용) | 네이버 커머스 API 조회/구현 시 **반드시 먼저 참조** — 웹 검색 전에 이 파일 확인 |

---

## 프로젝트 개요

**프로젝트명:** 완주베리 AI 운영 인사이트 시스템
**운영자:** 완주군 베리농가 (네이버 스마트스토어 + 쿠팡 판매)
**목적:** 농산물 도메인 특성을 반영한 AI 기반 운영 인사이트 시스템 구축

### 시스템 최종 목표
데이터 수집 → 분석 → 전략 제안 → 실행 → 피드백 루프를 반복하여
완주베리 농가 특성에 맞는 최적 마케팅 상태를 자동 유지한다.
운영자는 AI 제안을 승인/조정하는 파트너로 참여한다.
AI가 먼저 제안하고, 운영자가 생각해서 먼저 입력하는 구조는 없다.

### 핵심 철학
- Claude Code는 PDF를 직접 읽지 않는다
- AI 생성보다 검증 가능한 구조 우선
- Sample JSON 중심 개발
- 구조 안정성 > 최신 기술/추상화
- 일반 커머스 공식(CTR/CPC/ROAS)만으로 농산물을 해석하지 않는다
- 시즌을 모르면 광고 판단을 하지 않는다
- 운영자가 먼저 입력하는 구조를 만들지 않는다 (AI가 먼저 제안)

---

## 기술 스택 (확정)

| 레이어 | 기술 | 비고 |
|---|---|---|
| 프론트엔드 | React + Vite | Vercel 배포 |
| 백엔드 | Python FastAPI | Railway 배포 (Pro, Static IP) |
| 데이터베이스 | Supabase (PostgreSQL) | - |
| AI | Claude API (claude-sonnet-4-6) | Anthropic |
| 배포 | GitHub 연동 자동 배포 | push → 자동 빌드/배포 |

**Static IP 필수:** 네이버 커머스·광고·쿠팡 API 모두 호출 허용 IP 사전 등록 필요 → Railway Pro Static IP 사용

---

## 프론트엔드 메뉴 구조 (확정)

```
├── 대시보드     ← 읽기 전용. 마지막 수집 데이터 현황만 표시
├── 분석         ← [분석 시작] 버튼으로 수집~제안 전체 실행
├── 제안함       ← AI 제안 승인/거절 (72시간 만료 룰)
├── 실행 로그    ← Action Log 전체 이력
└── 설정
    ├── API 연결 상태  ← .env 키 기반, 연결 상태만 표시
    └── 시즌 날짜      ← 성수기/전환기 시작일 조정
```

**주요 원칙:**
- 수집 실행: 스케줄러 없음. 운영자가 분석 메뉴에서 직접 트리거
- API 키: .env 저장, UI에는 연결 상태만 노출
- 기준값: 설정 메뉴 아님 → AI가 계산 후 제안함으로 올림 → 운영자 승인 확정

---

## 전체 Phase 구조

```
Phase 1: API Knowledge Base 구축               ← ✅ 완료 (구조/템플릿) / 3종 세트는 Cowork 관리
Phase 2: 에이전트 구조 + Internal Model 설계   ← ✅ 완료
Phase 3: 실제 API 호출 + 오류 발견 + KB 수정  ← ✅ 완료 (네이버 커머스 + 네이버 광고)
Phase 4: 네이버 고도화 + 에이전트 구조 정비   ← 진행 중
  4-1: Railway + Vercel 배포                   ← ✅ 완료 (2026-05-18)
  4-2: 리뷰 API 연결                           ← ❌ 건너뜀 (네이버 커머스 API 공식 미지원)
  4-3: 광고 소재/카피 연동                     ← KB 완성 대기 중 (Cowork)
  4-4: 에이전트 폴더 구조 리팩터링             ← 4-3 완료 후
Phase 5: 쿠팡 에이전트 구현                    ← ✅ 완료 (2026-05-22)
  수집 / Brain / Validator / Wing 업로드 / Executor / 대시보드 전부 완료
Phase 6: 자동화 루프 고도화 (Learning Loop)   ← ✅ 완료 (2026-05-22)
  6-1: 거절 태그 UI ✅ / 6-2: Effect Tracker ✅ / 6-4: Brain 주입 ✅ / 6-5: Validator ✅
  6-C: Coupang Brain ✅ (전략모드/DEFEND/Executor/Wing UI 전부)
  6-3: Domain KB 빌더 ← 데이터 축적 후 구현 예정
```

---

## Phase 1 — API Knowledge Base

### 플랫폼별 KB 생성 방식
| 플랫폼 | 방식 | 관리 위치 |
|---|---|---|
| 네이버 커머스 API | llms.txt URL fetch → 자동 | Cowork |
| 네이버 검색광고 API | Swagger UI → PDF → 채팅 Claude → 3종 세트 | Cowork |
| 쿠팡 API | PDF → pdfplumber 혼합 추출 | Cowork |

**3종 세트 변환 작업은 이 프로젝트에서 제외 → Cowork에서 별도 관리**
완성된 KB 파일은 `backend/kb/` 폴더에 저장되면 에이전트가 읽는다.

---

## Phase 2 — 에이전트 구조 ✅ 완료

### 에이전트 구조 요약

```
오케스트레이터
├── 수집: naver_commerce / naver_ad / market_scan(stub)
├── 분석: product / ad / review(stub) / performance(stub)
└── 실행: executor (3단계 권한)
```

**설계 원칙:** 에이전트 간 직접 통신 금지 / 오케스트레이터 경유 / 항상 season_flag 먼저 확인

### 실행 권한 3단계

| 단계 | 예시 |
|---|---|
| AI 직접 실행 (승인 후) | 상품명 수정, 키워드 추가/제외, 광고 카피 수정, 입찰가 조정 |
| AI 제안 → 운영자 직접 실행 | 대표이미지 교체, 상세페이지 개편 |
| AI 제안 → 운영자 승인 → AI 실행 | 예산 증액, 캠페인 일시중지, 가격 조정 |

### 시즌 플래그 원칙
```
복분자 생과:  6월 중순 ~ 7월 초 / 블랙베리: 7월 ~ 8월
냉동 복분자:  연중 (피크: 추석/설 전후)
전환기:       성수기 2주 전 ~ 시즌 종료 1주 후
```
- 비수기 CTR/판매량 하락 → 광고 문제 아님, 자동 조정 트리거 금지
- 성과 비교는 전년 동기와만 비교

### 환경 세팅
- Python 가상환경: `backend/.venv` (Python 3.14)
- 패키지: FastAPI 0.136.1 / Pydantic 2.13.4 / Anthropic 0.102.0 / Supabase 2.30.0 / bcrypt / httpx
- 백엔드 실행: `cd backend && .venv\Scripts\python.exe -m uvicorn main:app --port 8000`
- 프론트 실행: `cd frontend && npm run dev` → http://localhost:5173 (또는 5174~5175)

---

## Phase 3 — 실제 API 연결 ✅ 완료

### 네이버 커머스 API

| 항목 | 내용 |
|---|---|
| 인증 | BCrypt.hashpw(`client_id_timestamp`, salt=`client_secret`) → Base64 |
| 토큰 | POST /external/v1/oauth2/token (type=SELF), 캐싱 적용 |
| 상품 목록 | POST /external/v1/products/search → channelProducts flat list |
| 주문 집계 | GET /external/v1/pay-order/seller/product-orders |
| 주문 API 제약 | from/to 최대 24시간 → 하루씩 루프, 0.5초 딜레이 (30일 = 약 15초) |
| 매칭 키 | 주문 productId = channelProductNo (originProductNo 아님) |

```python
# .env 필드
NAVER_COMMERCE_CLIENT_ID=
NAVER_COMMERCE_CLIENT_SECRET=   # 29자 bcrypt salt 그대로 사용
NAVER_COMMERCE_ACCOUNT_ID=
NAVER_COMMERCE_CHANNEL_NO=
```

### 네이버 검색광고 API

| 항목 | 내용 |
|---|---|
| 인증 | HMAC-SHA256(`timestamp.METHOD.path`, key=secret_key raw UTF-8) → Base64 |
| 서명 대상 | **base path만** 서명 (쿼리 파라미터 제외) |
| 베이스 URL | https://api.searchad.naver.com |
| 캠페인 | GET /ncc/campaigns |
| 광고그룹 | GET /ncc/adgroups?nccCampaignId={id} |
| 키워드 | GET /ncc/keywords?nccAdgroupId={id} |
| 성과 통계 | GET /stats — fields는 JSON 배열, timeRange는 ISO 날짜(YYYY-MM-DD) |
| 유효 통계 필드 | impCnt, clkCnt, salesAmt, ctr, cpc, convAmt, avgRnk |
| URL 인코딩 | urllib.parse.quote 사용 (urlencode 금지 — quote_plus가 JSON 깨뜨림) |

```python
# .env 필드
NAVER_AD_CUSTOMER_ID=
NAVER_AD_ACCESS_LICENSE=
NAVER_AD_SECRET_KEY=
```

### Supabase

| 항목 | 내용 |
|---|---|
| 키 | SUPABASE_SERVICE_ROLE_KEY 사용 (anon key는 RLS 차단) |
| 테이블 | analysis_runs / collected_products / suggestions / action_logs |
| collected_products | sales_revenue 컬럼 추가 완료 (bigint, default 0) |

### Suggestion action_type 전체 목록
```
상품명_수정 / 태그_추가 / 태그_수정 / 재입고_제안 / 가격_검토 / 이미지_교체
카피_수정 / 키워드_추가 / 키워드_제외 / 입찰가_조정 / 예산_조정 / 예산_증액 / 캠페인_일시중지
```

---

## Phase 4 — 다음 단계

우선순위 순:
1. ~~**Railway + Vercel 배포**~~ — ✅ 완료 (2026-05-18)
2. ~~**리뷰 API 연결**~~ — ❌ 건너뜀 (네이버 커머스 API 공식 미지원, review_count=0 유지)
3. **광고 키워드/카피 고도화** — 키워드별 성과 분석, 소재 제안
4. ~~**API데이터솔루션 신청**~~ — 사용 불가 (대안 방식 유지: 주문 집계 방식)
5. **쿠팡 API 연결**

---

## 도구 역할 분리

| 도구 | 역할 |
|---|---|
| Claude Code | 구조 설계, 핵심 구현, 에이전트 관리 |
| Cursor | 조회, 리뷰, 검색, 보조 분석 |
| 채팅 Claude | 기획, 전략, 오류 진단, 결정사항 정리 |
| Cowork | KB 3종 세트 변환/저장, 반복 파일 관리 |
