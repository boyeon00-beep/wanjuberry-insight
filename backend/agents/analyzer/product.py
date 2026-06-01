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

execution_tier 고정 규칙 (반드시 아래 값만 사용, 임의 변경 금지):
- 상품명_수정 → ai_auto
- 태그_추가 → ai_auto
- 태그_수정 → ai_auto
- 이미지_교체 → operator_manual
- 재입고_제안 → operator_manual
- 가격_검토 → operator_manual

상품명 수정 규칙:
- 최대 100자 초과 금지 (네이버 스마트스토어 제한)
- 권장 40자 내외 — 핵심 키워드 중심, 불필요한 수식어 제거
- 제안하는 상품명은 반드시 글자수를 함께 표기할 것 (예: "신규 상품명" (32자))
- 대괄호([]) 형식의 접두어 사용 금지 — 키워드는 자연스러운 문장 흐름에 녹일 것
- 동일 키워드 중복 금지 — 같은 단어가 상품명에 두 번 이상 등장하면 안 됨

베리 분류 원칙 (매우 중요):
- 각 상품의 berry_type 필드는 운영자가 직접 지정한 공식 분류다 — 상품명으로 추론 절대 금지
- berry_type이 "복분자"인 상품: 순수 복분자 상품이다. 블랙베리 관련 제안 금지
- berry_type이 "블랙베리"인 상품:
  · 실제 품종은 블랙베리다
  · 상품명에 "복분자"가 포함된 경우(예: 슈퍼복분자블랙베리)는 복분자 검색 노출을 위한
    의도적 크로스 작명 전략이다 — 상품명에서 복분자 키워드를 제거하는 제안 절대 금지
  · 태그/키워드 제안 시 권장 비율:
    블랙베리 직접 키워드 40~50% / 복분자 연관 키워드 30~40% / 용도·산지·용량 키워드 10~20%
  · 복분자 키워드는 유입 확장용으로 유지하되, 블랙베리 검색 노출이 누락되지 않도록 한다
  · 냉동생과 상품에 "복분자즙", "복분자원액", "복분자엑기스"처럼 가공품 구매 의도가 강한 키워드는 보수적으로 제안한다
- berry_type이 "미분류"이면 상품명을 참고하되, 혼동 위험이 있으면 제안을 보류한다

그룹상품 제안 규칙:
- product_id가 "GROUP-"으로 시작하면 그룹 전체를 대상으로 제안 1개만 생성 (variants 참고)
- target_id: product_id 그대로 사용 (예: "GROUP-12345")
- target_name: "상품명 [그룹 N종]" 형식 — 상품명은 name 필드 값, N은 member_count 값 사용 (예: member_count=3이면 "[그룹 3종]")
- execution_tier: 반드시 operator_manual (운영자가 판매자센터에서 그룹 전체 직접 적용)
- reason에 반드시 "그룹상품 공통 적용" 명시
- 상품명_수정 proposed_value 규칙: 그룹 대표명은 모든 variants를 아우르는 공통 이름이어야 한다.
  특정 용량(예: 1kg)이나 개수(예: 3개, 5개)를 포함하면 안 된다.
  current_value에는 현재 그룹 대표명(name 필드)을 그대로 표기한다.

하지 말아야 할 제안:
- 상품 데이터에 없는 인증, 무농약, 유기농, HACCP 문구 제안 금지
- 냉동생과 상품에 "생과 당일수확 배송"처럼 오해 가능한 문구 제안 금지
- 실제 판매하지 않는 용량/구성 제안 금지
- 리뷰 수가 적다는 이유만으로 리뷰 이벤트 제안 금지
- 비수기 판매 감소를 가격 문제로 단정 금지
- 데이터 없이 품질 문제, 포장 문제, 배송 문제를 단정 금지

제안 보류 원칙:
- 제안할 근거가 부족하거나 현재 운영 모드에서 실행할 필요가 없으면 빈 배열 []을 반환해도 된다
- 억지 제안보다 제안 보류가 우선이다
- 데이터에 없는 사실을 추정해서 제안하지 않는다"""

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
제약: 최대 10개 / 비수기 광고 성과 최적화 제안 금지 / 품절 상품은 시즌 재입고 안내만
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


def _cohort_block(patterns: list[dict], agent: str) -> str:
    relevant = [p for p in patterns if p.get("agent") == agent and p.get("total", 0) >= 3]
    if not relevant:
        return ""
    lines = "\n".join(
        f"- {p['action_type']}: 총 {p['total']}회 → positive {p['positive']}, "
        f"neutral {p['neutral']}, negative {p['negative']} (성공률 {p['positive_rate_pct']}%)"
        for p in relevant
    )
    return f"[과거 실적 패턴 — 성공률 높은 제안 우선, 낮은 제안은 보수적으로]\n{lines}\n\n"


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
    cohort_patterns   = context.get("cohort_patterns", [])

    products_summary   = _summarize_products(products)
    rejection_summary  = _summarize_rejections(rejection_history)
    effect_summary     = _summarize_effect_history(effect_history)

    user_msg = (
        _profile_block(context.get("farm_profile", ""))
        + _constraints_block(context.get("farm_constraints", []))
        + _cohort_block(cohort_patterns, "product_analyzer")
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
        max_tokens=8000,
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
    result = []
    for h in history:
        entry: dict = {
            "action_type":    h.get("action_type", ""),
            "target_name":    h.get("target_name", ""),
            "effect_verdict": h.get("effect_verdict", ""),
        }
        rm = h.get("result_metrics") or {}
        if rm.get("confidence") == "low":
            entry["note"] = "소량데이터_낮은신뢰도"
        if rm.get("compound_flag"):
            entry["note"] = entry.get("note", "") + " 복합실행"
        result.append(entry)
    return result


def _summarize_products(products: list[dict]) -> list[dict]:
    """Claude에 넘길 최소 필요 필드만 추출. 그룹상품은 groupProductNo 기준으로 묶어서 1개 엔트리로 반환"""
    from collections import defaultdict

    groups: dict[str, list] = defaultdict(list)
    individuals: list[dict] = []

    for p in products:
        gpn = p.get("group_product_no", "") or ""
        if gpn:
            groups[gpn].append(p)
        else:
            individuals.append(p)

    result = []

    for gpn, members in groups.items():
        rep = members[0]
        prices = sorted({m["price"] for m in members})
        price_str = (
            f"{prices[0]:,.0f}원 ~ {prices[-1]:,.0f}원" if len(prices) > 1
            else f"{prices[0]:,.0f}원"
        )
        result.append({
            "product_id":        f"GROUP-{gpn}",
            "is_group":          True,
            "member_count":      len(members),
            "variants":          [m["name"] for m in members],
            "name":              rep.get("group_product_name") or rep["name"],
            "berry_type":        rep.get("berry_type") or "미분류",
            "price_range":       price_str,
            "sales_count":       sum(m["sales_count"] for m in members),
            "sales_revenue":     sum(m.get("sales_revenue", 0) for m in members),
            "review_count":      rep["review_count"],
            "review_score":      rep["review_score"],
            "category":          rep["category"],
            "tags":              rep.get("tags", []),
            "stock":             sum(sum(opt["stock"] for opt in m.get("options", [])) for m in members),
            "product_type":      rep["domain"]["product_type"],
            "weight_kg":         rep["domain"]["weight_kg"],
            "unit_price_per_kg": rep["domain"]["unit_price_per_kg"],
        })

    for p in individuals:
        result.append({
            "product_id":        p["product_id"],
            "name":              p["name"],
            "berry_type":        p.get("berry_type") or "미분류",
            "price":             p["price"],
            "sales_count":       p["sales_count"],
            "review_count":      p["review_count"],
            "review_score":      p["review_score"],
            "category":          p["category"],
            "tags":              p.get("tags", []),
            "stock":             sum(opt["stock"] for opt in p.get("options", [])),
            "product_type":      p["domain"]["product_type"],
            "weight_kg":         p["domain"]["weight_kg"],
            "unit_price_per_kg": p["domain"]["unit_price_per_kg"],
        })

    return result
