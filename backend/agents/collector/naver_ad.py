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

    raw_campaigns = client.get_campaigns()
    campaign_ids  = [c["nccCampaignId"] for c in raw_campaigns]

    # 캠페인 성과 통계
    stats_by_id: dict[str, dict] = {}
    if campaign_ids:
        stats_list = client.get_campaign_stats(campaign_ids, start_date, end_date)
        for s in stats_list:
            stats_by_id[s["id"]] = s.get("stat", {})

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

    # 키워드 성과 통계
    if all_keyword_ids:
        kw_stats_list = client.get_keyword_stats(all_keyword_ids, start_date, end_date)
        kw_stats_by_id = {s["id"]: s.get("stat", {}) for s in kw_stats_list}
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

    return {
        "source":    "naver_ad",
        "mode":      "real",
        "total":     len(models),
        "campaigns": [m.model_dump() for m in models],
        "total_ad_copies": len(all_copies),
        "ad_copies": [c.model_dump() for c in all_copies],
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
        )
        for kw in keywords
    ]

    copy_items = [
        AdCopyItem(
            ad_id=c.get("nccAdId", ""),
            adgroup_id=c.get("nccAdgroupId", ""),
            campaign_id=campaign["nccCampaignId"],
            headline=c.get("headline", ""),
            description1=c.get("description", ""),
            description2=c.get("description2", ""),
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
    }


def _load_sample() -> dict:
    with open(_SAMPLE_PATH, encoding="utf-8") as f:
        return json.load(f)
