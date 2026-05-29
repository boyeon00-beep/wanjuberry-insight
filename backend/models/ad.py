from pydantic import BaseModel
from typing import Literal


class KeywordItem(BaseModel):
    keyword: str
    bid: float
    rank: int
    score: float
    clicks: int = 0
    impressions: int = 0
    sales_amt: float = 0.0


class AdCopyItem(BaseModel):
    ad_id: str
    adgroup_id: str
    campaign_id: str
    headline: str
    description1: str
    description2: str
    ad_type: str
    status: str


class AdDomain(BaseModel):
    season_flag: Literal["성수기", "비수기", "전환기"]
    season_adjusted_roas: float
    keyword_groups: list[Literal["브랜드형", "기능형", "고민해결형", "비교추천형", "시즌이벤트형"]]


class AdModel(BaseModel):
    campaign_id: str
    campaign_name: str
    platform: Literal["naver_searchad"]
    status: Literal["운영중", "일시중지", "종료"]
    budget_daily: float
    spend: float
    impressions: int
    clicks: int
    ctr: float
    cpc: float
    conversions: int
    roas: float
    keywords: list[KeywordItem] = []
    ad_copies: list["AdCopyItem"] = []
    domain: AdDomain
    collected_at: str
