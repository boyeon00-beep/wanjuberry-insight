import json

from anthropic import AsyncAnthropic
from models.suggestion import Suggestion

_client = AsyncAnthropic()

_SYSTEM = """당신은 완주베리 농가(네이버 검색광고) AI 광고 전문가입니다.

분석 원칙:
- 농산물 광고는 시즌 없이 CTR/ROAS만으로 판단하지 않는다
- 비수기에는 광고 예산 절감 및 유지 관리 제안만 한다 (성과 최적화 제안 금지)
- 전환기/성수기에는 입찰가 조정, 키워드 추가, 예산 확대를 구체적 수치로 제안한다
- 노출 순위 3위 이하 + CTR 3% 이상 키워드는 입찰가 인상을 우선 검토한다
- 노출 순위 1~2위 + CTR 1% 미만 키워드는 키워드 품질 또는 소재 문제를 의심한다
- ROAS가 낮더라도 비수기 브랜드 노출 유지 목적의 키워드는 유지를 권장한다
- 거절된 제안과 동일한 방향의 수정은 명확한 근거 없이 반복하지 않는다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

완주베리 네이버 검색광고 현황 (최근 30일):

{campaigns_json}

현재 운영 중인 광고 소재 (카피):

{ad_copies_json}

최근 거절/만료된 제안 이력:

{rejection_history_json}

위 광고 데이터를 분석하고 운영 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 성과 최적화 제안 금지 / 구체적 수치 포함
카피 소재가 있는 경우 카피_수정 제안을 반드시 1개 이상 포함하세요.
거절 이력이 있으면 그 이유를 반영해 다른 각도의 제안을 하세요.

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "캠페인 또는 광고 ID",
    "target_name": "캠페인명 또는 광고 소재명",
    "action_type": "입찰가_조정|키워드_추가|키워드_제외|예산_조정|예산_증액|캠페인_일시중지|카피_수정",
    "current_value": "현재 값",
    "proposed_value": "제안 값 (구체적 수치 또는 수정 카피 텍스트 포함)",
    "reason": "제안 이유 (시즌 컨텍스트 포함)",
    "priority": "high|medium|low",
    "execution_tier": "ai_auto|operator_manual|ai_after_approval"
  }}
]"""


def _constraints_block(constraints: list[dict]) -> str:
    if not constraints:
        return ""
    lines = "\n".join(f"- {c['content']}" for c in constraints)
    return f"[운영자 확인 팩트 — 절대 위반 금지]\n{lines}\n\n"


async def analyze(context: dict) -> dict:
    campaigns = context.get("collected_campaigns", [])
    if not campaigns:
        return {"suggestions": [], "note": "수집된 광고 캠페인 없음"}

    season_flag      = context.get("season_flag", "비수기")
    season_note      = context.get("season_note", "")
    task_id          = context.get("task_id", "unknown")
    ad_copies        = context.get("collected_ad_copies", [])
    rejection_history = context.get("ad_rejection_history", [])

    campaigns_summary = _summarize_campaigns(campaigns)
    ad_copies_summary = _summarize_ad_copies(ad_copies)
    rejection_summary = _summarize_rejections(rejection_history)

    user_msg = _constraints_block(context.get("farm_constraints", [])) + _USER_TEMPLATE.format(
        season_flag=season_flag,
        season_note=season_note,
        campaigns_json=json.dumps(campaigns_summary, ensure_ascii=False, indent=2),
        ad_copies_json=json.dumps(ad_copies_summary, ensure_ascii=False, indent=2),
        rejection_history_json=json.dumps(rejection_summary, ensure_ascii=False, indent=2),
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
        Suggestion(task_id=task_id, agent="ad_analyzer", **item)
        for item in raw_list
    ]

    return {
        "suggestions":    [s.model_dump() for s in suggestions],
        "total":          len(suggestions),
        "input_tokens":   response.usage.input_tokens,
        "output_tokens":  response.usage.output_tokens,
    }


def _summarize_campaigns(campaigns: list[dict]) -> list[dict]:
    return [
        {
            "campaign_id":   c["campaign_id"],
            "campaign_name": c["campaign_name"],
            "status":        c["status"],
            "budget_daily":  c["budget_daily"],
            "spend":         c["spend"],
            "impressions":   c["impressions"],
            "clicks":        c["clicks"],
            "ctr":           c["ctr"],
            "cpc":           c["cpc"],
            "conversions":   c["conversions"],
            "roas":          c["roas"],
            "keywords": [
                {
                    "keyword": kw["keyword"],
                    "bid":     kw["bid"],
                    "rank":    kw["rank"],
                    "ctr":     kw["score"],
                }
                for kw in c.get("keywords", [])
            ],
        }
        for c in campaigns
    ]


def _summarize_ad_copies(ad_copies: list[dict]) -> list[dict]:
    if not ad_copies:
        return []
    return [
        {
            "ad_id":        c.get("ad_id", ""),
            "campaign_id":  c.get("campaign_id", ""),
            "headline":     c.get("headline", ""),
            "description1": c.get("description1", ""),
            "description2": c.get("description2", ""),
            "status":       c.get("status", ""),
        }
        for c in ad_copies
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
