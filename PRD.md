# 완주베리 AI 운영 인사이트 시스템 — PRD.md

> 기능 명세 문서. 에이전트별 상세 스펙, 인터페이스, 대시보드, 데이터 모델.
> 에이전트 구현 시 반드시 읽는다.

---

## 1. 분석 대상 범위

| 분석 대상 | 담당 에이전트 | 분석 내용 |
|---|---|---|
| 광고 성과 | 광고 분석 에이전트 | CTR, CPC, ROAS, 키워드 효율 (시즌 보정 적용) |
| 판매 성과 | 성과 통합 에이전트 | 채널별 판매량, 매출 추이, 전년 동기 대비 |
| 상품명 | 상품 분석 에이전트 | SEO 키워드 포함 여부, 경쟁상품 대비 구성, 검색 노출 최적화 |
| 상세페이지 | 상품 분석 에이전트 | 구조, 소구점, 시즌 메시지 적합성 (제안만, AI 직접 수정 불가) |
| 리뷰 | 리뷰 분석 에이전트 | 반복 키워드, 불만 패턴, 칭찬 포인트 → 상품명/카피 개선 제안 |
| 시장/경쟁 | 시장스캔 에이전트 | 경쟁상품 순위/가격/리뷰 변화, 키워드 시장 트렌드 |

---

## 2. 에이전트 상세 스펙

### 오케스트레이터
- 전체 흐름 제어, 에이전트 호출 순서 결정
- 모든 분석/실행 전 season_flag 먼저 확인
- 사용자 승인 요청 및 결과 대시보드 반영

### 수집 레이어
| 에이전트 | 수집 데이터 | 주기 |
|---|---|---|
| 네이버커머스 수집 | 상품/판매/리뷰 데이터 | 매일 |
| 네이버광고 수집 | 캠페인/키워드/성과 데이터 | 매일 |
| 시장스캔 | 경쟁사/키워드/시장 데이터 | 매일 00:03 |

### 분석 레이어
| 에이전트 | 주요 역할 |
|---|---|
| 상품 분석 | 상품명 SEO, 상세페이지 구조, 경쟁상품 비교 → 수정 제안 |
| 광고 분석 | 캠페인 효율, 키워드/카피 제안 (시즌 인식 필수) |
| 리뷰 분석 | 반복 키워드, 불만/칭찬 패턴 → 상품명/카피 개선 제안 |
| 성과 통합 | 판매+광고 통합 해석, 월 리포트 생성 |

### 실행 에이전트 (단일)
- 모든 API 호출 전담
- 실패 포함 모든 실행 결과 Action Log에 기록
- 롤백 관리

---

## 3. 에이전트 인터페이스 표준

### 입력
```json
{
  "task_id": "string",
  "agent": "string",
  "action": "string",
  "params": {},
  "context": {
    "season_flag": "성수기 | 비수기 | 전환기",
    "triggered_by": "schedule | user | orchestrator"
  },
  "requested_at": "ISO8601"
}
```

### 출력
```json
{
  "task_id": "string",
  "agent": "string",
  "status": "success | error | pending_approval",
  "data": {},
  "suggestions": [
    {
      "suggestion_id": "string",
      "type": "상품수정 | 광고수정 | 캠페인생성 | 예산조정 | 키워드추가 | 키워드제외 | 카피수정",
      "execution_type": "ai_direct | user_direct | ai_after_approval",
      "description": "string",
      "requires_approval": true,
      "payload": {}
    }
  ],
  "errors": [],
  "completed_at": "ISO8601"
}
```

---

## 4. 사용자 승인 플로우

```
분석 에이전트 → 제안 생성 (status: pending_approval)
       ↓
오케스트레이터 → 대시보드 제안함에 표시
       ↓
사용자 → 승인 / 거절
       ↓ (승인 시)
오케스트레이터 → 실행 에이전트 호출
       ↓
실행 에이전트 → API 호출 → Action Log 기록
       ↓
오케스트레이터 → 결과 대시보드 반영
```

**승인 대기 제한:** 72시간 후 자동 만료. 만료 시 Action Log에 "만료" 기록.

**대시보드 제안 표시 원칙:**
- "AI가 직접 처리할게요 (승인만 해주세요)"
- "이렇게 수정해보세요 (직접 하셔야 해요)"
- "승인하시면 제가 처리할게요"

---

## 5. Action Log 구조

```json
{
  "log_id": "string",
  "task_id": "string",
  "agent": "string",
  "action_type": "상품수정 | 광고수정 | 캠페인생성 | 예산조정 | 키워드추가 | 키워드제외 | 카피수정",
  "suggestion_id": "string",
  "approved_by": "user | auto",
  "status": "success | failed | rolled_back | expired",
  "payload_sent": {},
  "response_received": {},
  "error": "string | null",
  "rollback_available": true,
  "executed_at": "ISO8601",
  "season_flag": "string"
}
```

**원칙:** 실행 에이전트만 기록 / 실패도 반드시 기록 / season_flag 항상 포함

---

## 6. Internal Model 스키마

### ProductModel
```json
{
  "product_id": "string",
  "platform": "naver | coupang",
  "name": "string",
  "price": "number",
  "options": [{ "name": "string", "price_delta": "number", "stock": "number" }],
  "sales_count": "number",
  "review_count": "number",
  "review_score": "number",
  "category": "string",
  "tags": ["string"],
  "domain": {
    "product_type": "생과 | 냉동 | 즙 | 가공품",
    "weight_kg": "number",
    "unit_price_per_kg": "number",
    "season_flag": "성수기 | 비수기 | 전환기"
  },
  "collected_at": "ISO8601"
}
```

### AdModel
```json
{
  "campaign_id": "string",
  "campaign_name": "string",
  "platform": "naver_searchad",
  "status": "운영중 | 일시중지 | 종료",
  "budget_daily": "number",
  "spend": "number",
  "impressions": "number",
  "clicks": "number",
  "ctr": "number",
  "cpc": "number",
  "conversions": "number",
  "roas": "number",
  "keywords": [{ "keyword": "string", "bid": "number", "rank": "number", "score": "number" }],
  "domain": {
    "season_flag": "성수기 | 비수기 | 전환기",
    "season_adjusted_roas": "number",
    "keyword_groups": ["브랜드형 | 기능형 | 고민해결형 | 비교추천형 | 시즌이벤트형"]
  },
  "collected_at": "ISO8601"
}
```

### MarketModel
```json
{
  "keyword": "string",
  "search_volume_pc": "number",
  "search_volume_mobile": "number",
  "clicks": "number",
  "ctr": "number",
  "avg_cpc": "number",
  "competition_level": "높음 | 중간 | 낮음",
  "keyword_score": "number",
  "keyword_type": "메인 | 세부 | 구매의도 | 제외",
  "competitors": [
    { "product_name": "string", "price": "number", "review_count": "number", "review_score": "number", "rank": "number" }
  ],
  "snapshot_date": "ISO8601",
  "domain": {
    "season_flag": "성수기 | 비수기 | 전환기",
    "market_trend": "string"
  }
}
```

---

## 7. 대시보드 구성 스펙

| 섹션 | 데이터 소스 | 업데이트 주기 |
|---|---|---|
| 시즌 현황 | Domain KB seasonality | 실시간 |
| 광고비 현황 | 네이버광고 수집 에이전트 | 매일 |
| 채널별 판매량 | 네이버커머스/쿠팡 수집 에이전트 | 매일 |
| 키워드 현황 | 시장스캔 에이전트 | 매일 |
| 시장현황 | 시장스캔 에이전트 | 매일 |
| AI 제안함 | 분석 에이전트 출력 | 실시간 |
| 실행 로그 | Action Log | 실시간 |
| 월 리포트 | 성과 통합 에이전트 | 월 1회 |

---

## 8. 광고 키워드/카피 엔진 (Phase 4 선행 설계)

### 광고 세팅 흐름

```
[트리거: 전환기 진입 감지 (성수기 2주 전)]
       ↓
1. 상품 정보 로드 (ProductModel)
2. LLM 키워드 후보 생성
   - 메인: 복분자, 냉동복분자, 블랙베리
   - 세부: 복분자 효능, 완주 복분자, 국산 블랙베리
   - 구매의도: 복분자 구매, 복분자즙 추천, 블랙베리 주문
   - 제외: 무료, 부작용, 논문, 병원
3. 네이버 검색광고 API 데이터 조회 (검색수/CPC/경쟁강도)
4. 키워드 점수화 (keyword-rules.md 기준)
5. 광고그룹 자동 구성 (브랜드형/기능형/고민해결형/비교추천형/시즌이벤트형)
6. LLM 광고 카피 생성 (제목 + 설명문 + 확장소재)
       ↓
오케스트레이터 → 운영자 승인 요청
       ↓ (승인 시)
실행 에이전트 → 캠페인/광고그룹/카피 등록
```

### 성과 피드백 루프 (Phase 4 2차)

```
광고 집행 후 성과 수집
  - CTR 낮음   → 광고 카피 수정 제안
  - CPC 높음   → 입찰가 조정 제안
  - 전환 없음  → 해당 키워드 제외 제안
  - ROAS 좋음  → 예산 증액 제안
  - 모바일 성과 좋음 → 모바일 입찰가 상향 제안
모든 제안은 운영자 승인 후 실행
```

---

## 9. performance-baselines.md 구조

```
## 기준값 메타
- 최초 설정일: YYYY-MM-DD
- 기반 데이터 기간: YYYY-MM-DD ~ YYYY-MM-DD
- 마지막 검토일: YYYY-MM-DD
- 다음 검토 예정: 시즌 종료 후 자동 트리거

## 지표별 기준값
| 시즌 | 상품유형 | 지표 | 기준값 | 판단 |
|---|---|---|---|---|
| 성수기 | 복분자 생과 | ROAS | 300% | 이상: 좋음 / 이하: 검토 |
| 성수기 | 복분자 생과 | CTR | 2.5% | 이상: 좋음 / 이하: 카피 검토 |
| 비수기 | 냉동 복분자 | ROAS | - | 비교 안 함 (전년 동기만) |

## 조정 이력
- YYYY-MM-DD: [지표] [이전값] → [변경값] / 사유: [운영자 메모]
```

**운영 원칙:**
- AI가 먼저 계산 후 제안, 운영자가 직접 입력하는 구조 없음
- 비수기 지표는 기준값 설정 안 함
- 기준값 변경 시 조정 이력 필수 기록
- 데이터 부족 시 "데이터 부족 - 1시즌 후 재설정" 표시
