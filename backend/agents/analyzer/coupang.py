import json

from anthropic import AsyncAnthropic
from models.suggestion import Suggestion

_client = AsyncAnthropic()

_SYSTEM = """당신은 완주베리 농가(쿠팡) AI 운영 전문가입니다.

첫 번째 질문: "이 상품은 쿠팡에서 팔릴 준비가 됐는가?"

상품 준비도 평가 기준 (현재 수집 가능한 데이터만 사용):
- 상품명: 쿠팡 소비자가 바로 이해할 수 있는가
- 가격: kg당 단가가 상품 유형 대비 지나치게 불리하지 않은가
- 매출 반응: 최근 30일 실제 구매가 있는가 (sales_count, sales_revenue)
- 시즌 적합성: 현재 시즌에 맞는 상품인가

절대 언급하지 않는 항목:
- 재고 수량 (실제 재고 미수집 — stock=0은 시스템 고정값)
- 리뷰·평점 (쿠팡 Open API 미지원)
- 대표이미지 상태 (이미지 URL 미수집)
- 이미지_교체 제안 (이미지 현황 파악 불가)
- Wing 데이터 없을 때 광고비·클릭·전환·ROAS 언급

전략 모드별 판단 원칙:
- READY_CHECK: 매출 없음 또는 불명확 → 상품명·가격 정비 우선, 확장 제안 금지
- TEST: 매출 일부 있음 → 판매 반응 관찰, 소폭 개선 제안만
- SCALE: 매출 꾸준히 확인 → 유지·강화 방향 제안 가능
- DEFEND: 광고 클릭은 있으나 14일 전환 0 → 상품 페이지·가격·구성 문제 의심
  · 가격 인하 / 상품명 개선 / 상품 구성 변경 제안 우선
  · 광고 끄기·예산 조정 제안 금지 (그건 Wing에서 운영자가 직접)
  · Wing 데이터(clicks, orders_14d, ad_cost, roas_14d)를 근거로 구체적으로 설명
- RANK_GUARD: 랭킹 조작·외부 업체 유혹성 제안은 즉시 거부

농산물 원칙:
- 비수기 하락은 운영 문제 아님 — 자동 확장·프로모션 제안 금지
- 단순 가격 인하만 제안하지 않는다 — 쿠팡 수수료(약 10~15%) 고려 후 제안
- 성과 비교는 전년 동기와만 한다
- 제안은 즉시 실행 가능한 수준으로 구체적이어야 한다

베리 분류 원칙 (매우 중요):
- 각 상품의 berry_type 필드는 운영자가 직접 지정한 공식 분류다 — 상품명으로 추론 절대 금지
- berry_type이 "복분자"인 상품에 블랙베리 관련 제안을 하지 않는다
- berry_type이 "블랙베리"인 상품에 복분자 관련 제안을 하지 않는다
- berry_type이 "미분류"이면 상품명을 참고하되, 혼동 위험이 있으면 제안을 보류한다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

현재 쿠팡 전략 모드: {coupang_strategy_mode}

완주베리 쿠팡 상품 현황 (최근 30일):

{products_json}

Wing 광고 보고서 데이터 (업로드된 경우):

{wing_json}

최근 거절/만료된 제안 이력 (rejection_tag 포함):

{rejection_history_json}

최근 성과 측정 이력:

{effect_history_json}

위 상품들을 분석하고 현재 쿠팡 전략 모드({coupang_strategy_mode})에 맞는 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 대규모 프로모션 제안 금지 / 구체적 수치 포함 / 이미지·광고 끄기·재고·리뷰 관련 제안 금지
DEFEND 모드: Wing 데이터의 클릭·전환 수치를 reason에 명시하고 상품 페이지 개선 위주로 제안하세요.
거절 이력의 rejection_tag를 반드시 참고하세요: '여력없음'은 재제안 가능, '이미시도해봤음'은 재제안 금지.

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "상품 ID (sellerProductId)",
    "target_name": "상품명",
    "action_type": "가격_검토|재입고_제안|상품명_수정|태그_추가",
    "current_value": "현재 값",
    "proposed_value": "제안 값 (구체적 수치 포함)",
    "reason": "제안 이유 (시즌 + 쿠팡 전략 모드 + 상품 준비도 반영)",
    "priority": "high|medium|low",
    "execution_tier": "ai_auto|operator_manual|ai_after_approval"
  }}
]"""


def _profile_block(profile: str) -> str:
    if not profile or not profile.strip():
        return ""
    return f"[농장 프로필]\n{profile.strip()}\n\n"


def _constraints_block(constraints: list[dict]) -> str:
    if not constraints:
        return ""
    lines = "\n".join(f"- {c['content']}" for c in constraints)
    return f"[운영자 확인 팩트 — 절대 위반 금지]\n{lines}\n\n"


async def analyze(context: dict) -> dict:
    products = context.get("coupang_products", [])
    if not products:
        return {"suggestions": [], "note": "수집된 쿠팡 상품 없음"}

    season_flag       = context.get("season_flag", "비수기")
    season_note       = context.get("season_note", "")
    task_id           = context.get("task_id", "unknown")
    rejection_history = context.get("coupang_rejection_history", [])

    coupang_strategy_mode = context.get("coupang_strategy_mode", "READY_CHECK")
    effect_history        = context.get("coupang_effect_history", [])
    wing_data             = context.get("coupang_ad_summary", [])

    products_summary   = _summarize_products(products)
    rejection_summary  = _summarize_rejections(rejection_history)
    effect_summary     = _summarize_effect_history(effect_history)
    wing_summary       = _summarize_wing_data(wing_data)

    user_msg = (
        _profile_block(context.get("farm_profile", ""))
        + _constraints_block(context.get("farm_constraints", []))
        + _USER_TEMPLATE.format(
            season_flag=season_flag,
            season_note=season_note,
            coupang_strategy_mode=coupang_strategy_mode,
            products_json=json.dumps(products_summary, ensure_ascii=False, indent=2),
            wing_json=json.dumps(wing_summary, ensure_ascii=False, indent=2) if wing_summary else "없음",
            rejection_history_json=json.dumps(rejection_summary, ensure_ascii=False, indent=2),
            effect_history_json=json.dumps(effect_summary, ensure_ascii=False, indent=2),
        )
    )

    response = await _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```", 2)[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        raw_list = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude 응답 파싱 실패: {e}\n원문: {raw_text!r}") from e

    suggestions = [
        Suggestion(task_id=task_id, agent="coupang_analyzer", **item)
        for item in raw_list
    ]

    return {
        "suggestions":   [s.model_dump() for s in suggestions],
        "total":         len(suggestions),
        "input_tokens":  response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def _summarize_products(products: list[dict]) -> list[dict]:
    return [
        {
            "product_id":        p["product_id"],
            "name":              p["name"],
            "berry_type":        p.get("berry_type") or "미분류",
            "price":             p["price"],
            "sales_count":       p["sales_count"],
            "sales_revenue":     p["sales_revenue"],
            "product_type":      p["domain"]["product_type"],
            "weight_kg":         p["domain"]["weight_kg"],
            "unit_price_per_kg": p["domain"]["unit_price_per_kg"],
        }
        for p in products
    ]


def _summarize_rejections(history: list[dict]) -> list[dict]:
    if not history:
        return []
    return [
        {
            "target_name":    r.get("target_name", ""),
            "action_type":    r.get("action_type", ""),
            "proposed_value": r.get("proposed_value", ""),
            "rejection_tag":  r.get("rejection_tag") or "태그없음",
            "status":         r.get("status", ""),
        }
        for r in history
    ]


def _summarize_wing_data(wing_data: list[dict]) -> list[dict]:
    if not wing_data:
        return []
    return [
        {
            "product_name":           r.get("product_name", ""),
            "report_period":          f"{r.get('report_from','')} ~ {r.get('report_to','')}",
            "impressions":            r.get("impressions", 0),
            "clicks":                 r.get("clicks", 0),
            "ad_cost":                r.get("ad_cost", 0),
            "orders_14d":             r.get("orders_14d", 0),
            "conversion_revenue_14d": r.get("conversion_revenue_14d", 0),
            "roas_14d":               r.get("roas_14d"),
        }
        for r in wing_data
    ]


def _summarize_effect_history(history: list[dict]) -> list[dict]:
    if not history:
        return []
    return [
        {
            "action_type":    h.get("action_type", ""),
            "target_name":    h.get("target_name", ""),
            "effect_verdict": h.get("effect_verdict", ""),
        }
        for h in history
    ]
