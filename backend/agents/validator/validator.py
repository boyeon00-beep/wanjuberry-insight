import json

from anthropic import AsyncAnthropic

_client = AsyncAnthropic()

_SYSTEM = """당신은 완주베리 AI 시스템의 Ad Strategy Validator입니다.

역할: 분석 에이전트가 생성한 후보 제안을 검증하여 제안함 등록 여부를 판정합니다.
제안을 다시 생성하지 않습니다. 이미 생성된 제안을 기준표로 검토합니다.

판정 기준 10가지:
1. 현재 시즌과 제안이 맞는가?
2. 검색 수요 증가를 광고 성과로 오판하지 않았는가?
3. 광고 전략 모드와 제안이 맞는가?
4. 상품 유형과 제안이 맞는가?
5. 키워드 의도 유형이 적절한가?
6. 플랫폼 역할과 맞는가?
7. 운영자 과거 거절 패턴과 충돌하지 않는가? ('이미시도해봤음' 태그는 BLOCK)
8. 재고·수확·농번기 부담을 고려했는가?
9. 성과 측정 기준이 action_type과 전략모드에 맞는가?
10. 데이터가 부족한데 강한 제안을 하지 않았는가?

판정 4종:
- PASS: 제안함 등록 가능
- WARN: 등록 가능하나 주의 문구 필요
- BLOCK: 등록 금지
- NEEDS_DATA: 데이터 부족 — 관찰 항목 전환

전략 모드별 BLOCK 기준:
- PREPARE: 예산_증액·입찰가 공격적 상승·캠페인_일시중지 → BLOCK
- TEST: 대규모 예산 확대, SCALE 수준 확장 → BLOCK
- SCALE: 재고 부족 상황의 무제한 확장 → WARN
- 비수기에 성과 최적화 제안 → BLOCK
- 거절 이력 중 '이미시도해봤음'과 동일한 action_type + target → BLOCK"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
현재 전략 모드: {ad_strategy_mode}

최근 거절 이력 요약 (rejection_tag 포함):
{rejection_summary}

검증할 후보 제안 목록:
{suggestions_json}

각 제안에 대해 판정하세요.
PASS는 note 빈 문자열, WARN·BLOCK·NEEDS_DATA는 한 문장 이유 필수.

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "suggestion_id": "...",
    "verdict": "PASS|WARN|BLOCK|NEEDS_DATA",
    "note": "판정 이유"
  }}
]"""


async def validate(suggestions: list[dict], context: dict) -> dict[str, dict]:
    """
    후보 제안을 검증하여 {suggestion_id: {verdict, note}} 반환.
    Claude API 호출 1회로 전체 배치 처리.
    """
    if not suggestions:
        return {}

    season_flag      = context.get("season_flag", "비수기")
    ad_strategy_mode = context.get("ad_strategy_mode", "PREPARE")

    # 거절 이력 (전체 에이전트 통합)
    all_rejections = (
        context.get("ad_rejection_history", []) +
        context.get("product_rejection_history", []) +
        context.get("coupang_rejection_history", [])
    )
    rejection_summary = _summarize_rejections(all_rejections)

    # 제안 요약 (검증에 필요한 최소 필드)
    suggestions_compact = [
        {
            "suggestion_id": s["suggestion_id"],
            "agent":         s["agent"],
            "action_type":   s["action_type"],
            "target_name":   s["target_name"],
            "current_value": s["current_value"],
            "proposed_value": s["proposed_value"],
            "reason":        s["reason"],
            "priority":      s["priority"],
            "is_repeat":     s.get("is_repeat", False),
        }
        for s in suggestions
    ]

    user_msg = _USER_TEMPLATE.format(
        season_flag=season_flag,
        ad_strategy_mode=ad_strategy_mode,
        rejection_summary=json.dumps(rejection_summary, ensure_ascii=False, indent=2),
        suggestions_json=json.dumps(suggestions_compact, ensure_ascii=False, indent=2),
    )

    response = await _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
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
        results = json.loads(raw_text)
    except json.JSONDecodeError:
        # 파싱 실패 시 모두 PASS 처리 (검증 실패가 분석 전체를 막지 않도록)
        return {s["suggestion_id"]: {"verdict": "PASS", "note": ""} for s in suggestions}

    return {
        r["suggestion_id"]: {
            "verdict": r.get("verdict", "PASS"),
            "note":    r.get("note", ""),
        }
        for r in results
        if "suggestion_id" in r
    }


def _summarize_rejections(history: list[dict]) -> list[dict]:
    if not history:
        return []
    return [
        {
            "target_name":   r.get("target_name", ""),
            "action_type":   r.get("action_type", ""),
            "rejection_tag": r.get("rejection_tag") or "태그없음",
        }
        for r in history
    ]
