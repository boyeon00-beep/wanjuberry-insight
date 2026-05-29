import json
import os
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

from models.ad import AdCopyItem, AdDomain, AdModel, KeywordItem

_SAMPLE_PATH = Path(__file__).parent / "sample_data" / "naver_ad_sample.json"

_STATUS_MAP = {
    "ELIGIBLE": "운영중",
    "PAUSED":   "일시중지",
    "ENDED":    "종료",
}


async def collect(context: dict) -> dict:
    use_real = bool(os.environ.get("NAVER_AD_CUSTOMER_ID"))
    if use_real:
        return await _collect_real(context)
    return _collect_mock(context)


# --- Real ---

async def _collect_real(context: dict) -> dict:
    from clients import naver_ad as client

    season_flag  = context.get("season_flag", "비수기")
    collected_at = datetime.now(timezone.utc).isoformat()

    today      = date.today()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date   = today.strftime("%Y-%m-%d")

    all_campaigns = client.get_campaigns()
    raw_campaigns = [c for c in all_campaigns if c.get("status") in ("ELIGIBLE", "PAUSED")]
    campaign_ids  = [c["nccCampaignId"] for c in raw_campaigns]

    # 캠페인 성과 통계 (날짜별 다건 응답인 경우 캠페인ID 기준 합산)
    stats_by_id: dict[str, dict] = {}
    if campaign_ids:
        stats_list = client.get_campaign_stats(campaign_ids, start_date, end_date)
        for s in stats_list:
            cid = s["id"]
            st  = s.get("stat", {})
            if cid not in stats_by_id:
                stats_by_id[cid] = {"impCnt": 0, "clkCnt": 0, "salesAmt": 0.0, "convAmt": 0.0}
            stats_by_id[cid]["impCnt"]   += int(float(st.get("impCnt", 0)))
            stats_by_id[cid]["clkCnt"]   += int(float(st.get("clkCnt", 0)))
            stats_by_id[cid]["salesAmt"] += float(st.get("salesAmt", 0))
            stats_by_id[cid]["convAmt"]  += float(st.get("convAmt", 0))
        # CTR · CPC는 합산 후 재계산
        for cid, s in stats_by_id.items():
            imp, clk = s["impCnt"], s["clkCnt"]
            s["ctr"] = round(clk / imp * 100, 2) if imp > 0 else 0.0
            s["cpc"] = round(s["salesAmt"] / clk, 0) if clk > 0 else 0.0

    # 키워드·광고소재 수집 (캠페인 → 광고그룹 → 키워드/소재)
    keywords_by_campaign: dict[str, list[dict]] = {cid: [] for cid in campaign_ids}
    ad_copies_by_campaign: dict[str, list[dict]] = {cid: [] for cid in campaign_ids}
    all_keyword_ids: list[str] = []
    keyword_to_campaign: dict[str, str] = {}

    for campaign in raw_campaigns:
        cid = campaign["nccCampaignId"]
        adgroups = client.get_adgroups(cid)
        for ag in adgroups:
            ag_id = ag["nccAdgroupId"]
            kws = client.get_keywords(ag_id)
            for kw in kws:
                kid = kw["nccKeywordId"]
                all_keyword_ids.append(kid)
                keyword_to_campaign[kid] = cid
                keywords_by_campaign[cid].append(kw)

            copies = client.get_ads(ag_id)
            for copy in copies:
                ad_copies_by_campaign[cid].append({**copy, "nccAdgroupId": ag_id, "nccCampaignId": cid})

    # 키워드 성과 통계 (날짜별 다건 응답 → 키워드별 합산)
    if all_keyword_ids:
        kw_stats_list = client.get_keyword_stats(all_keyword_ids, start_date, end_date)
        kw_stats_by_id: dict[str, dict] = {}
        for s in kw_stats_list:
            kid = s["id"]
            st  = s.get("stat", {})
            if kid not in kw_stats_by_id:
                kw_stats_by_id[kid] = {"impCnt": 0, "clkCnt": 0, "salesAmt": 0.0, "avgRnk": 0.0, "_cnt": 0}
            kw_stats_by_id[kid]["impCnt"]   += int(float(st.get("impCnt", 0)))
            kw_stats_by_id[kid]["clkCnt"]   += int(float(st.get("clkCnt", 0)))
            kw_stats_by_id[kid]["salesAmt"] += float(st.get("salesAmt", 0))
            kw_stats_by_id[kid]["avgRnk"]   += float(st.get("avgRnk", 0))
            kw_stats_by_id[kid]["_cnt"]     += 1
        # avgRnk는 평균
        for s in kw_stats_by_id.values():
            cnt = s.pop("_cnt", 1) or 1
            s["avgRnk"] = round(s["avgRnk"] / cnt, 2)
            imp, clk = s["impCnt"], s["clkCnt"]
            s["ctr"] = round(clk / imp * 100, 2) if imp > 0 else 0.0
        for cid, kws in keywords_by_campaign.items():
            for kw in kws:
                kw["stats"] = kw_stats_by_id.get(kw["nccKeywordId"], {})

    models = [
        _raw_to_ad_model(
            c,
            stats_by_id.get(c["nccCampaignId"], {}),
            keywords_by_campaign.get(c["nccCampaignId"], []),
            ad_copies_by_campaign.get(c["nccCampaignId"], []),
            season_flag,
            collected_at,
        )
        for c in raw_campaigns
    ]

    all_copies = _flatten_ad_copies(models)

    # 키워드 검색량 + 연관 키워드 조회
    # 현재 입찰 중인 키워드 + 농장 기본 시드
    bidding_keywords = list({
        kw.get("keyword", "")
        for cid, kws in keywords_by_campaign.items()
        for kw in kws
        if kw.get("keyword")
    })
    seed_keywords = _build_seed_keywords(bidding_keywords)
    keyword_tool_data = client.get_keyword_tool(seed_keywords)
    kw_volume_list = [_normalize_kw_volume(k) for k in keyword_tool_data]

    return {
        "source":    "naver_ad",
        "mode":      "real",
        "total":     len(models),
        "campaigns": [m.model_dump() for m in models],
        "total_ad_copies": len(all_copies),
        "ad_copies": [c.model_dump() for c in all_copies],
        "keyword_volume": kw_volume_list,
    }


def _raw_to_ad_model(
    campaign: dict,
    stats: dict,
    keywords: list[dict],
    raw_copies: list[dict],
    season_flag: str,
    collected_at: str,
) -> AdModel:
    imp   = int(stats.get("impCnt", 0))
    clk   = int(stats.get("clkCnt", 0))
    spend = float(stats.get("salesAmt", 0))
    conv  = 0
    rev   = float(stats.get("convAmt", 0))

    ctr  = round(clk / imp * 100, 2) if imp > 0 else 0.0
    cpc  = round(spend / clk, 0)    if clk > 0 else 0.0
    roas = round(rev / spend * 100, 1) if spend > 0 else 0.0

    kw_items = [
        KeywordItem(
            keyword=kw.get("keyword", ""),
            bid=float(kw.get("bidAmt", 0)),
            rank=int(kw.get("stats", {}).get("avgRnk", 0)),
            score=float(kw.get("stats", {}).get("ctr", 0)),
            clicks=int(kw.get("stats", {}).get("clkCnt", 0)),
            impressions=int(kw.get("stats", {}).get("impCnt", 0)),
            sales_amt=float(kw.get("stats", {}).get("salesAmt", 0.0)),
        )
        for kw in keywords
    ]

    copy_items = [
        AdCopyItem(
            ad_id=c.get("nccAdId", ""),
            adgroup_id=c.get("nccAdgroupId", ""),
            campaign_id=campaign["nccCampaignId"],
            headline=_extract_ad_text(c, "headline"),
            description1=_extract_ad_text(c, "description"),
            description2=_extract_ad_text(c, "description2"),
            ad_type=c.get("type", ""),
            status=_STATUS_MAP.get(c.get("status", ""), c.get("status", "")),
        )
        for c in raw_copies
    ]

    return AdModel(
        campaign_id=campaign["nccCampaignId"],
        campaign_name=campaign.get("name", ""),
        platform="naver_searchad",
        status=_STATUS_MAP.get(campaign.get("status", ""), "운영중"),
        budget_daily=float(campaign.get("dailyBudget", 0)),
        spend=spend,
        impressions=imp,
        clicks=clk,
        ctr=ctr,
        cpc=cpc,
        conversions=conv,
        roas=roas,
        keywords=kw_items,
        ad_copies=copy_items,
        domain=AdDomain(
            season_flag=season_flag,
            season_adjusted_roas=roas,
            keyword_groups=[],
        ),
        collected_at=collected_at,
    )


def _extract_ad_text(c: dict, field: str) -> str:
    """Naver /ncc/ads 응답에서 텍스트 추출 — top-level 또는 adAttr 중첩 처리"""
    top = c.get(field, "")
    if top:
        return top
    ad_attr = c.get("adAttr", {})
    if isinstance(ad_attr, dict):
        return ad_attr.get(field, "")
    return ""


def _flatten_ad_copies(models: list[AdModel]) -> list[AdCopyItem]:
    result = []
    for m in models:
        result.extend(m.ad_copies)
    return result


# --- Mock ---

def _collect_mock(context: dict) -> dict:
    raw = _load_sample()
    season_flag  = context.get("season_flag", "비수기")
    collected_at = datetime.now(timezone.utc).isoformat()

    kws_by_campaign: dict[str, list[dict]] = {}
    for kw in raw.get("keywords", []):
        cid = kw["nccCampaignId"]
        kws_by_campaign.setdefault(cid, []).append(kw)

    ads_by_campaign: dict[str, list[dict]] = {}
    for ad in raw.get("ads", []):
        cid = ad["nccCampaignId"]
        ads_by_campaign.setdefault(cid, []).append(ad)

    models = [
        _raw_to_ad_model(
            c,
            c.get("stats", {}),
            kws_by_campaign.get(c["nccCampaignId"], []),
            ads_by_campaign.get(c["nccCampaignId"], []),
            season_flag,
            collected_at,
        )
        for c in raw["campaigns"]
    ]

    all_copies = _flatten_ad_copies(models)

    return {
        "source":    "naver_ad",
        "mode":      "mock",
        "total":     len(models),
        "campaigns": [m.model_dump() for m in models],
        "total_ad_copies": len(all_copies),
        "ad_copies": [c.model_dump() for c in all_copies],
        "keyword_volume": [],
    }


# 완주베리 농장 핵심 시드 키워드 — 검색량 조회 기준점
_FARM_SEED_KEYWORDS = ["복분자", "블랙베리", "냉동복분자", "복분자즙"]


def _build_seed_keywords(bidding_keywords: list[str]) -> list[str]:
    """현재 입찰 키워드 + 농장 기본 시드 → 중복 제거 후 최대 5개"""
    combined = _FARM_SEED_KEYWORDS + [
        kw for kw in bidding_keywords if kw not in _FARM_SEED_KEYWORDS
    ]
    return combined[:5]


def _normalize_kw_volume(raw: dict) -> dict:
    """Naver keywordstool 응답 정규화 — '< 10' 처리"""
    from clients.naver_ad import _parse_qc_cnt
    pc     = _parse_qc_cnt(raw.get("monthlyPcQcCnt", 0))
    mobile = _parse_qc_cnt(raw.get("monthlyMobileQcCnt", 0))
    return {
        "keyword":       raw.get("relKeyword", ""),
        "monthly_pc":    pc,
        "monthly_mobile": mobile,
        "monthly_total": pc + mobile,
        "competition":   raw.get("compIdx", ""),  # 낮음|보통|높음
    }


def _load_sample() -> dict:
    with open(_SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)
