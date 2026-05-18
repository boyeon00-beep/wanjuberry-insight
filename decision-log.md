# decision-log.md — 완주베리 AI 운영 인사이트 시스템

> 결정 이력 전체 기록. 맥락 확인 필요 시 읽는다.
> 결정사항 변경 시 이 파일 먼저 수정 → CLAUDE.md / ARCHITECTURE.md 반영.

---

## 2026-05-17

### [D-001] 기술 스택 확정
- **결정:** React + Vercel / FastAPI + Railway Pro / Supabase
- **배경:** 네이버 커머스·광고·쿠팡 API 모두 호출 허용 IP 사전 등록 필수. Railway Pro Static IP가 유일하게 네이티브 지원하며 이전 프로젝트에서 검증됨.
- **검토한 대안:** Render (Static IP 네이티브 미지원, QuotaGuard 프록시 필요 → 복잡도 증가로 제외)
- **확정 스택:**
  - 프론트엔드: React + Vercel
  - 백엔드: FastAPI + Railway (Pro, Static IP)
  - DB: Supabase (PostgreSQL)
  - AI: Claude API
  - 배포: GitHub 연동 자동 배포

---

### [D-002] 3종 세트 작업 범위 제외
- **결정:** API KB 3종 세트 변환 작업은 이 프로젝트에서 제외, Cowork에서 별도 관리
- **배경:** 운영자가 Cowork으로 직접 변환/저장 관리하는 게 더 효율적
- **영향:** Phase 1 완료 기준에서 "P0 API 전체 3종 세트 완성" 항목 제외. 폴더 구조와 conversion-template.md만 이 프로젝트에서 관리.

---

### [D-003] 수집 실행 방식 — 스케줄러 제외, 버튼 방식 채택
- **결정:** 자동 스케줄러 없음. 운영자가 분석 메뉴에서 "분석 시작" 버튼으로 직접 트리거
- **배경:**
  - Railway 상시 실행 비용 절감
  - 농업 특성상 매일 자동 수집이 필수가 아님 (성수기 자주, 비수기 가끔)
  - CLAUDE.md 철학 "운영자가 파트너"와 일치
- **영향:** APScheduler 제거, FastAPI 단순화

---

### [D-004] 메뉴 구조 확정
- **결정:** 대시보드 / 분석 / 제안함 / 실행 로그 / 설정
- **세부 결정:**
  - 대시보드: 읽기 전용 현황 표시 (버튼 없음)
  - 분석: 실행 트리거 + 결과 표시
  - 설정: API 연결 상태 + 시즌 날짜만 (API 키는 .env 저장, UI엔 연결 상태만 노출)
  - 기준값(performance-baselines): 설정 메뉴 아님 → AI가 제안함으로 올림 → 운영자 승인

---

### [D-005] 기준값 관리 방식
- **결정:** AI가 먼저 계산 → 제안함으로 올림 → 운영자 승인으로 확정
- **배경:** PRD 원칙 "AI가 먼저 제안, 운영자가 직접 입력하는 구조 없음" 유지
- **흐름:**
  1. Phase 3 첫 분석 실행 시 AI가 과거 데이터 기반 기준값 자동 계산
  2. 제안함에 "기준값 초안 승인 요청"으로 노출
  3. 운영자 승인 → performance-baselines 확정
  4. 이후 시즌 종료마다 AI가 재검토 제안

---

## 2026-05-18

### [D-006] Railway + Vercel 배포 완료
- **결정:** Railway Pro (Static IP) + Vercel 배포 구조 확정 및 완료
- **배포 정보:**
  - 백엔드: https://wanjuberry-insight-production.up.railway.app
  - 프론트엔드: https://wanjuberry-insight.vercel.app
  - Static IP: 162.220.232.99 (네이버 커머스 API 허용 등록 완료)
- **환경변수 구조:**
  - Railway: CORS_ORIGIN=https://wanjuberry-insight.vercel.app
  - Vercel: VITE_API_URL=https://wanjuberry-insight-production.up.railway.app

---

### [D-007] Phase 4 작업 순서 확정
- **결정:** 아래 순서로 진행
  1. 리뷰 API 연결 (네이버 커머스 API, 별도 신청 불필요)
  2. 광고 소재/카피 연동 (KB 파일 완성 후 — Cowork에서 작업 중)
  3. 에이전트 폴더 구조 리팩터링 (네이버/쿠팡 분리)
  4. 쿠팡 에이전트 구현
- **제외 항목:** API데이터솔루션 — 브랜드스토어 전용, 현재 해당 없음

---

### [D-008] 에이전트 폴더 구조 리팩터링 시점
- **결정:** 쿠팡 연동 전에 리팩터링 먼저 완료 후 쿠팡 구현
- **배경:** 지금 리팩터링하면 동작 중인 네이버 연동 전체 임포트 경로가 바뀌어 리스크가 큼. 네이버 작업 완료 후 독립적인 리팩터링 단계로 분리하는 게 안전함
- **목표 구조:**
  ```
  agents/
  ├── naver/
  │   ├── collector/  (commerce.py, ad.py)
  │   └── analyzer/   (product.py, ad.py)
  ├── coupang/
  │   ├── collector/  (commerce.py)
  │   └── analyzer/   (product.py, revenue.py)
  └── executor/       (공통 유지)
  ```
- **임시 방편:** 리팩터링 전까지 쿠팡 파일은 `coupang_` 접두사로 기존 폴더에 추가하지 않음 (쿠팡 구현 자체를 리팩터링 이후로 미룸)
