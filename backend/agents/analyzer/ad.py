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
- ROAS가 낮더라도 비수기 브랜드 노출 유지 목적의 키워드는 유지를 권장한다"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

완주베리 네이버 검색광고 현황 (최근 30일):

{campaigns_json}

위 광고 데이터를 분석하고 운영 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 비수기 성과 최적화 제안 금지 / 구체적 수치 포함

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "캠페인 또는 키워드 ID",
    "target_name": "캠페인명 또는 키워드",
    "action_type": "입찰가_조정|키워드_추가|키워드_제외|예산_조정|예산_증액|캠페인_일시중지|카피_수정",
    "current_value": "현재 값",
    "proposed_value": "제안 값 (구체적 수치 포함)",
    "reason": "제안 이유 (시즌 컨텍스트 포함)",
    "priority": "high|medium|low",
    "execution_tier": "ai_auto|operator_manual|ai_after_approval"
  }}
]"""


async def analyze(context: dict) -> dict:
    campaigns = context.get("collected_campaigns", [])
    if not campaigns:
        return {"suggestions": [], "note": "수집된 광고 캠페인 없음"}

    season_flag = context.get("season_flag", "비수기")
    season_note = context.get("season_note", "")
    task_id     = context.get("task_id", "unknown")

    campaigns_summary = _summarize_campaigns(campaigns)

    user_msg = _USER_TEMPLATE.format(
        season_flag=season_flag,
        season_note=season_note,
        campaigns_json=json.dumps(campaigns_summary, ensure_ascii=False, indent=2),
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
