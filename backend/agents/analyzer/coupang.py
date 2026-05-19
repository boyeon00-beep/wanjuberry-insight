import json

from anthropic import AsyncAnthropic
from models.suggestion import Suggestion

_client = AsyncAnthropic()

_SYSTEM = """당신은 완주베리 농가(쿠팡) AI 운영 전문가입니다.

분석 원칙:
- 쿠팡은 최저가 경쟁이 핵심 — 매출이 낮은 상품은 가격 경쟁력부터 검토한다
- 농산물은 시즌에 따라 판매량이 자연히 변동한다 — 비수기 하락을 운영 문제로 오해하지 않는다
- 판매 수량이 0이더라도 시즌 외 상품이면 재입고 제안만 한다
- 쿠팡 수수료(서비스이용료)를 고려한 실질 정산금액 관점으로 가격을 분석한다
- 비수기에는 가격 유지 또는 소폭 인하 제안만 한다 (대규모 프로모션 제안 금지)
- 제안은 즉시 실행 가능한 수준으로 구체적이어야 한다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

완주베리 쿠팡 상품 현황 (최근 30일):

{products_json}

최근 거절/만료된 제안 이력:

{rejection_history_json}

위 상품들을 분석하고 운영 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 대규모 프로모션 제안 금지 / 구체적 수치 포함

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "상품 ID (sellerProductId)",
    "target_name": "상품명",
    "action_type": "가격_검토|재입고_제안|이미지_교체|상품명_수정|태그_추가",
    "current_value": "현재 값",
    "proposed_value": "제안 값 (구체적 수치 포함)",
    "reason": "제안 이유 (시즌 컨텍스트 + 쿠팡 특성 반영)",
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

    products_summary   = _summarize_products(products)
    rejection_summary  = _summarize_rejections(rejection_history)

    user_msg = (
        _profile_block(context.get("farm_profile", ""))
        + _constraints_block(context.get("farm_constraints", []))
        + _USER_TEMPLATE.format(
            season_flag=season_flag,
            season_note=season_note,
            products_json=json.dumps(products_summary, ensure_ascii=False, indent=2),
            rejection_history_json=json.dumps(rejection_summary, ensure_ascii=False, indent=2),
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
            "product_id":      p["product_id"],
            "name":            p["name"],
            "price":           p["price"],
            "sales_count":     p["sales_count"],
            "sales_revenue":   p["sales_revenue"],
            "product_type":    p["domain"]["product_type"],
            "weight_kg":       p["domain"]["weight_kg"],
            "unit_price_per_kg": p["domain"]["unit_price_per_kg"],
        }
        for p in products
    ]


def _summarize_rejections(history: list[dict]) -> list[dict]:
    if not history:
        return []
    return [
        {
            "target_id":      r.get("target_id", ""),
            "target_name":    r.get("target_name", ""),
            "action_type":    r.get("action_type", ""),
            "proposed_value": r.get("proposed_value", ""),
            "reason":         r.get("reason", ""),
            "status":         r.get("status", ""),
            "created_at":     r.get("created_at", ""),
        }
        for r in history
    ]
