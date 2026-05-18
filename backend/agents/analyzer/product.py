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
- 제안은 즉시 실행 가능한 수준으로 구체적이어야 한다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

완주베리 스마트스토어 상품 현황:

{products_json}

위 상품들을 분석하고 운영 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 광고 성과 최적화 제안 금지 / 품절 상품은 시즌 재입고 안내만

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "상품 ID",
    "target_name": "상품명",
    "action_type": "상품명_수정|태그_추가|태그_수정|재입고_제안|가격_검토|이미지_교체",
    "current_value": "현재 값",
    "proposed_value": "제안 값",
    "reason": "제안 이유 (시즌 컨텍스트 포함)",
    "priority": "high|medium|low",
    "execution_tier": "ai_auto|operator_manual|ai_after_approval"
  }}
]"""


async def analyze(context: dict) -> dict:
    products = context.get("collected_products", [])
    if not products:
        return {"suggestions": [], "note": "수집된 상품 없음"}

    season_flag = context.get("season_flag", "비수기")
    season_note = context.get("season_note", "")
    task_id = context.get("task_id", "unknown")

    products_summary = _summarize_products(products)

    user_msg = _USER_TEMPLATE.format(
        season_flag=season_flag,
        season_note=season_note,
        products_json=json.dumps(products_summary, ensure_ascii=False, indent=2),
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


def _summarize_products(products: list[dict]) -> list[dict]:
    """Claude에 넘길 최소 필요 필드만 추출"""
    return [
        {
            "product_id": p["product_id"],
            "name": p["name"],
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
