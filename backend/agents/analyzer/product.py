import json
import os

from anthropic import AsyncAnthropic
from models.suggestion import Suggestion

_client = AsyncAnthropic()  # ANTHROPIC_API_KEY 환경변수 자동 사용

_SYSTEM = """당신은 완주베리 농가(네이버 스마트스토어) AI 운영 전문가입니다.

분석 원칙:
- 농산물은 시즌에 따라 판매량이 자연히 변동한다 — 비수기 하락을 광고 문제로 해석하지 않는다
- 비수기에는 냉동 복분자 중심 운영을 권장하고, 광고 성과 최적화 제안은 보류한다
- 성수기(복분자 생과 6/15~7/7, 블랙베리 7/15~8/31) 진입 전 전환기에 선제 제안한다
- 품절 상품은 해당 시즌 개시 전 재입고를 안내한다
- 제안은 즉시 실행 가능한 수준으로 구체적이어야 한다

베리 분류 원칙 (매우 중요):
- 각 상품의 berry_type 필드는 운영자가 직접 지정한 공식 분류다 — 상품명으로 추론 절대 금지
- berry_type이 "복분자"인 상품에 블랙베리 관련 제안을 하지 않는다
- berry_type이 "블랙베리"인 상품에 복분자 관련 제안을 하지 않는다
- berry_type이 "미분류"이면 상품명을 참고하되, 혼동 위험이 있으면 제안을 보류한다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

현재 운영 모드: {ad_strategy_mode}
(PREPARE=준비정비 / TEST=소폭변경테스트 / SCALE=적극개선 / DEFEND=현상유지 / REVIEW=회고)

완주베리 스마트스토어 상품 현황:

{products_json}

최근 거절/만료된 제안 이력 (rejection_tag 포함):

{rejection_history_json}

최근 성과 측정 이력:

{effect_history_json}

위 상품들을 분석하고 현재 운영 모드({ad_strategy_mode})에 맞는 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 광고 성과 최적화 제안 금지 / 품절 상품은 시즌 재입고 안내만
거절 이력의 rejection_tag를 반드시 참고하세요: '여력없음'은 재제안 가능, '이미시도해봤음'은 재제안 금지.

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "상품 ID",
    "target_name": "상품명",
    "action_type": "상품명_수정|태그_추가|태그_수정|재입고_제안|가격_검토|이미지_교체",
    "current_value": "현재 값",
    "proposed_value": "제안 값",
    "reason": "제안 이유 (시즌 + 운영모드 포함)",
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
    products = context.get("collected_products", [])
    if not products:
        return {"suggestions": [], "note": "수집된 상품 없음"}

    season_flag = context.get("season_flag", "비수기")
    season_note = context.get("season_note", "")
    task_id = context.get("task_id", "unknown")

    ad_strategy_mode  = context.get("ad_strategy_mode", "PREPARE")
    rejection_history = context.get("product_rejection_history", [])
    effect_history    = context.get("product_effect_history", [])

    products_summary   = _summarize_products(products)
    rejection_summary  = _summarize_rejections(rejection_history)
    effect_summary     = _summarize_effect_history(effect_history)

    user_msg = (
        _profile_block(context.get("farm_profile", ""))
        + _constraints_block(context.get("farm_constraints", []))
        + _USER_TEMPLATE.format(
            season_flag=season_flag,
            season_note=season_note,
            ad_strategy_mode=ad_strategy_mode,
            products_json=json.dumps(products_summary, ensure_ascii=False, indent=2),
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
    # 마크다운 코드블록 제거 (```json ... ``` 또는 ``` ... ```)
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
        Suggestion(task_id=task_id, agent="product_analyzer", **item)
        for item in raw_list
    ]

    return {
        "suggestions": [s.model_dump() for s in suggestions],
        "total": len(suggestions),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


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


def _summarize_products(products: list[dict]) -> list[dict]:
    """Claude에 넘길 최소 필요 필드만 추출"""
    return [
        {
            "product_id": p["product_id"],
            "name": p["name"],
            "berry_type": p.get("berry_type") or "미분류",
            "price": p["price"],
            "sales_count": p["sales_count"],
            "review_count": p["review_count"],
            "review_score": p["review_score"],
            "category": p["category"],
            "tags": p["tags"],
            "stock": sum(opt["stock"] for opt in p.get("options", [])),
            "product_type": p["domain"]["product_type"],
            "weight_kg": p["domain"]["weight_kg"],
            "unit_price_per_kg": p["domain"]["unit_price_per_kg"],
        }
        for p in products
    ]
