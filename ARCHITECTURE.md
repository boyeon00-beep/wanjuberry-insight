# 완주베리 AI 운영 인사이트 시스템 — ARCHITECTURE.md

> 기술 스택, 폴더 구조, 데이터 흐름, 배포 구조.
> 구현 시작 시 반드시 읽는다.

---

## 1. 프론트엔드 메뉴 구조

```
├── 대시보드          ← 홈. 마지막 수집 데이터 현황만 표시 (버튼 없음)
│   ├── 시즌 현황 (성수기 / 비수기 / 전환기)
│   ├── 매출 / 주문건수 (채널별)
│   ├── 광고비 / ROAS
│   └── 키워드 조회수 Top5
│
├── 분석              ← [분석 시작] 버튼으로 수집~제안 전체 실행
│   ├── 상품 분석 결과
│   ├── 광고 분석 결과
│   ├── 리뷰 분석 결과
│   └── 시장/경쟁 현황
│
├── 제안함            ← AI 제안 승인/거절 (72시간 만료 룰)
│   ├── 대기중
│   ├── 승인됨
│   └── 만료/거절
│
├── 실행 로그         ← Action Log 전체 이력
│
└── 설정
    ├── API 연결 상태  ← .env 키 기반, 연결 성공/실패 상태만 표시
    └── 시즌 날짜      ← 성수기/전환기 시작일 직접 조정
```

**설계 원칙:**
- 대시보드: 읽기 전용, 마지막 수집 데이터 표시
- 분석 실행: 분석 메뉴에서만 트리거 (스케줄러 없음, 운영자가 필요할 때 실행)
- 기준값(performance-baselines): 설정 메뉴 아님 → AI가 계산 후 제안함으로 올림 → 운영자 승인으로 확정
- API 키: .env 저장, UI에는 연결 상태만 노출

---

## 2. 기술 스택

| 레이어 | 기술 | 비고 |
|---|---|---|
| 프론트엔드 | React + Vite | Vercel 배포 |
| 백엔드 | Python FastAPI | Railway 배포 (Pro, Static IP) |
| 데이터베이스 | Supabase (PostgreSQL) | - |
| AI | Claude API (claude-sonnet) | Anthropic |
| 배포 | GitHub 연동 자동 배포 | push → 자동 빌드/배포 |

### Static IP 필수 이유
네이버 커머스 API, 네이버 검색광고 API, 쿠팡 API 모두 호출 허용 IP를 사전 등록해야 한다.
Railway Pro Static IP를 사용하면 재배포 시에도 IP가 변경되지 않는다.

---

## 2. 레포지토리 구조

```
wanjuberry-ai/
├── backend/                        ← FastAPI (Railway 배포)
│   ├── main.py                     ← FastAPI 앱 진입점
│   ├── orchestrator/
│   │   └── orchestrator.py         ← 전체 흐름 제어
│   ├── agents/
│   │   ├── collector/
│   │   │   ├── naver_commerce.py   ← 네이버 커머스 수집
│   │   │   ├── naver_ad.py         ← 네이버 검색광고 수집
│   │   │   └── market_scan.py      ← 시장스캔 수집
│   │   ├── analyzer/
│   │   │   ├── product.py          ← 상품 분석
│   │   │   ├── ad.py               ← 광고 분석
│   │   │   ├── review.py           ← 리뷰 분석
│   │   │   └── performance.py      ← 성과 통합
│   │   └── executor/
│   │       └── executor.py         ← 단일 실행 에이전트
│   ├── models/
│   │   ├── product.py              ← ProductModel
│   │   ├── ad.py                   ← AdModel
│   │   └── market.py               ← MarketModel
│   ├── db/
│   │   └── supabase_client.py      ← Supabase 연결
│   ├── kb/                         ← API Knowledge Base (Cowork에서 관리)
│   │   ├── _index.md
│   │   ├── naver-searchad/
│   │   ├── naver-commerce/
│   │   └── coupang/
│   ├── domain/
│   │   └── seasonality.py          ← 시즌 플래그 계산
│   └── requirements.txt
│
├── frontend/                       ← React (Vercel 배포)
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard.jsx       ← 메인 대시보드
│   │   └── components/
│   │       ├── SuggestionBox.jsx   ← AI 제안함
│   │       └── ActionLog.jsx       ← 실행 로그
│   └── package.json
│
├── CLAUDE.md
├── ARCHITECTURE.md                 ← 이 파일
├── PRD.md
└── decision-log.md
```

---

## 3. 데이터 흐름

```
[스케줄러 / 사용자 트리거]
        ↓
[오케스트레이터]
  1. season_flag 확인 (seasonality.py)
  2. 수집 에이전트 호출
        ↓
[수집 에이전트] → 외부 API 호출 (Static IP 경유)
  - 네이버 커머스: 상품/판매/리뷰
  - 네이버 검색광고: 캠페인/키워드/성과
  - 시장스캔: 경쟁사/키워드
        ↓
[Supabase] ← 수집 데이터 저장
        ↓
[분석 에이전트] → Claude API 호출
  - ProductModel / AdModel / MarketModel 기반 분석
  - 제안 생성 (status: pending_approval)
        ↓
[오케스트레이터] → 대시보드 제안함 표시
        ↓
[운영자 승인]
        ↓
[실행 에이전트] → 외부 API 호출 → Action Log 기록
        ↓
[오케스트레이터] → 대시보드 결과 반영
```

---

## 4. 배포 구조

```
GitHub (단일 레포)
├── backend/ → Railway 자동 감지 → FastAPI 배포
└── frontend/ → Vercel 자동 감지 → React 배포
```

### 환경변수 관리
| 변수 | 위치 |
|---|---|
| NAVER_AD_API_KEY | Railway 환경변수 |
| NAVER_COMMERCE_API_KEY | Railway 환경변수 |
| COUPANG_API_KEY | Railway 환경변수 |
| SUPABASE_URL | Railway + Vercel 환경변수 |
| SUPABASE_KEY | Railway + Vercel 환경변수 |
| ANTHROPIC_API_KEY | Railway 환경변수 |

---

## 5. Supabase 테이블 구조 (초안)

| 테이블 | 내용 |
|---|---|
| products | ProductModel 수집 데이터 |
| ads | AdModel 수집 데이터 |
| market | MarketModel 수집 데이터 |
| suggestions | AI 제안 (pending_approval / approved / rejected / expired) |
| action_logs | 실행 에이전트 Action Log 전체 |
| performance_baselines | 시즌별 기준값 |

---

## 6. 에이전트 호출 원칙

- 에이전트 간 직접 통신 금지 → 반드시 오케스트레이터 경유
- 모든 에이전트 입력에 `season_flag` 포함 필수
- 실행 에이전트만 외부 API 쓰기(POST/PUT) 가능
- 수집/분석 에이전트는 읽기(GET)만 가능
- 실패 포함 모든 실행 결과 Action Log 기록 필수

---

## 7. 개발 순서 (Phase 2 구현 기준)

```
1. Supabase 테이블 생성
2. seasonality.py 구현 (season_flag 계산)
3. 오케스트레이터 기본 골격
4. 수집 에이전트 1개 (네이버 커머스) → sample.json 기반 mock 먼저
5. Internal Model (ProductModel) 구현
6. 분석 에이전트 1개 (상품 분석) → Claude API 연결
7. 실행 에이전트 골격 + Action Log
8. 대시보드 제안함 UI
```
