import json

from anthropic import AsyncAnthropic
from models.suggestion import Suggestion

_client = AsyncAnthropic()

_SYSTEM = """당신은 완주베리 농가(네이버 검색광고) AI 광고 전문가입니다.

분석 원칙:
- 농산물 광고는 시즌 없이 CTR/ROAS만으로 판단하지 않는다
- 성수기 매출 증가는 성공이 아니라 기본값일 수 있다 — 시장 수요 증가분을 넘는 성과를 만들었는지 봐야 한다
- 노출 순위 3위 이하 + CTR 3% 이상 키워드는 입찰가 인상을 우선 검토한다
- 노출 순위 1~2위 + CTR 1% 미만 키워드는 키워드 품질 또는 소재 문제를 의심한다
- ROAS가 낮더라도 비수기 브랜드 노출 유지 목적의 키워드는 유지를 권장한다

광고 전략 모드별 제안 원칙 (현재 모드는 프롬프트에 명시됨):
- PREPARE: 키워드/카피/광고구조 정비만. 예산 확대·성과 최적화 제안 금지
- TEST: 소액 키워드 5~10개 테스트, 소폭 입찰가 조정, CTR 반응 확인이 목표
- SCALE: 성과 키워드 집중, 예산 확대 가능, 전환금액 증가 목표 (단, 재고 한계 고려)
- DEFEND: 예산 안정화, CPC 높은 키워드 제한, 품절 위험 상품 광고 축소
- LEARN: 정보탐색형/활용법형 키워드 우선. 매출보다 소비자 반응 발견이 목표
- REVIEW: 다음 시즌 대비 패턴 정리, 성과/실패 키워드 구분 제안

키워드 의도 유형 (제안 시 반드시 구분):
- 구매형: 냉동복분자구매, 복분자판매 → 바로 전환
- 활용법형: 복분자청만들기, 블랙베리스무디 → 수요 확대
- 정보탐색형: 블랙베리효능, 복분자먹는법 → 인지도 형성
- 시즌형: 명절선물복분자, 여름베리청 → 시즌 수요
- 브랜드형: 완주베리, 완주복분자 → 신뢰/재방문
- 비교형: 복분자블랙베리차이 → 낮은 인지도 보완
- 부적합형: 무료, 묘목, 목적불일치 → 제외 후보

거절 태그 해석 (거절 이력 반영 시 참고):
- 시즌맞지않음: 해당 타이밍에 재시도하지 않음 (시즌이 바뀌면 재제안 가능)
- 이미시도해봤음: 동일 방향 재제안 금지
- 방향이다름: 다른 각도의 제안 필요
- 여력없음: 제안 품질 문제 아님 — 동일 방향으로 재제안 가능
- 기타: 메모 없으면 판단 유보

execution_tier 고정 규칙 (반드시 아래 값만 사용, 임의 변경 금지):
- 입찰가_조정 → ai_auto
- 키워드_추가 → ai_auto
- 키워드_제외 → ai_auto
- 카피_수정 → ai_auto
- 예산_조정 → ai_auto
- 예산_증액 → ai_after_approval
- 캠페인_일시중지 → ai_after_approval"""

_USER_TEMPLATE = """현재 시즌: {season_flag}
{season_note}

현재 광고 전략 모드: {ad_strategy_mode}
(PREPARE=준비 / TEST=소액테스트 / SCALE=확장 / DEFEND=방어 / LEARN=학습 / REVIEW=회고)

완주베리 네이버 검색광고 현황 (최근 30일):

{campaigns_json}

현재 운영 중인 광고 소재 (카피):

{ad_copies_json}

키워드 월간 검색량 (현재 입찰 키워드 + 연관 키워드):

{keyword_volume_json}

최근 거절/만료된 제안 이력 (rejection_tag 포함):

{rejection_history_json}

최근 성과 측정 이력 (승인된 제안의 실제 효과):

{effect_history_json}

위 광고 데이터를 분석하고 현재 전략 모드({ad_strategy_mode})에 맞는 운영 개선 제안을 JSON 배열로 반환하세요.
제약: 최대 5개 / 현재 전략 모드에 맞지 않는 제안 금지 / 구체적 수치 포함
카피 소재가 있는 경우 카피_수정 제안을 반드시 1개 이상 포함하세요.
키워드 검색량이 있는 경우, 검색량이 높으나 입찰하지 않는 연관 키워드는 키워드_추가로 제안하세요.
거절 이력의 rejection_tag를 반드시 참고하세요: '여력없음'은 재제안 가능, '이미시도해봤음'은 재제안 금지.
성과 이력이 있으면 positive 패턴을 강화하고 negative 패턴은 회피하세요.

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "target_id": "캠페인 또는 광고 ID",
    "target_name": "캠페인명 또는 광고 소재명",
    "action_type": "입찰가_조정|키워드_추가|키워드_제외|예산_조정|예산_증액|캠페인_일시중지|카피_수정",
    "current_value": "현재 값",
    "proposed_value": "제안 값 (구체적 수치 또는 수정 카피 텍스트 포함)",
    "reason": "제안 이유 (시즌 + 전략모드 + 키워드의도유형 포함)",
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
    campaigns = context.get("collected_campaigns", [])
    if not campaigns:
        return {"suggestions": [], "note": "수집된 광고 캠페인 없음"}

    season_flag      = context.get("season_flag", "비수기")
    season_note      = context.get("season_note", "")
    task_id          = context.get("task_id", "unknown")
    ad_copies        = context.get("collected_ad_copies", [])
    rejection_history = context.get("ad_rejection_history", [])
    keyword_volume   = context.get("keyword_volume", [])

    ad_strategy_mode  = context.get("ad_strategy_mode", "PREPARE")
    effect_history    = context.get("ad_effect_history", [])

    campaigns_summary    = _summarize_campaigns(campaigns)
    ad_copies_summary    = _summarize_ad_copies(ad_copies)
    rejection_summary    = _summarize_rejections(rejection_history)
    kw_volume_summary    = _summarize_keyword_volume(keyword_volume, campaigns)
    effect_summary       = _summarize_effect_history(effect_history)

    user_msg = (
        _profile_block(context.get("farm_profile", ""))
        + _constraints_block(context.get("farm_constraints", []))
        + _USER_TEMPLATE.format(
            season_flag=season_flag,
            season_note=season_note,
            ad_strategy_mode=ad_strategy_mode,
            campaigns_json=json.dumps(campaigns_summary, ensure_ascii=False, indent=2),
            ad_copies_json=json.dumps(ad_copies_summary, ensure_ascii=False, indent=2),
            keyword_volume_json=json.dumps(kw_volume_summary, ensure_ascii=False, indent=2),
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


def _summarize_keyword_volume(volume_list: list[dict], campaigns: list[dict]) -> list[dict]:
    """검색량 데이터 요약 — 현재 입찰 여부 표시"""
    bidding_keywords = {
        kw.keyword.lower()
        for c in campaigns
        for kw in c.get("keywords", [])
        if hasattr(kw, "keyword")
    }
    # campaigns가 dict인 경우도 처리
    if campaigns and isinstance(campaigns[0], dict):
        bidding_keywords = {
            kw.get("keyword", "").lower()
            for c in campaigns
            for kw in c.get("keywords", [])
        }

    return sorted(
        [
            {
                "keyword":        v["keyword"],
                "monthly_total":  v["monthly_total"],
                "monthly_pc":     v["monthly_pc"],
                "monthly_mobile": v["monthly_mobile"],
                "competition":    v["competition"],
                "is_bidding":     v["keyword"].lower() in bidding_keywords,
            }
            for v in volume_list
            if v.get("keyword")
        ],
        key=lambda x: x["monthly_total"],
        reverse=True,
    )


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
            "created_at":     r.get("created_at", ""),
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
            "ad_strategy_mode": h.get("ad_strategy_mode", ""),
            "executed_at":    h.get("executed_at", ""),
        }
        for h in history
    ]
