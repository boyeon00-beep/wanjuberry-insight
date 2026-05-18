from pydantic import BaseModel
from typing import Literal


class Competitor(BaseModel):
    product_name: str
    price: float
    review_count: int
    review_score: float
    rank: int


class MarketDomain(BaseModel):
    season_flag: Literal["성수기", "비수기", "전환기"]
    market_trend: str


class MarketModel(BaseModel):
    keyword: str
    search_volume_pc: int
    search_volume_mobile: int
    clicks: int
    ctr: float
    avg_cpc: float
    competition_level: Literal["높음", "중간", "낮음"]
    keyword_score: float
    keyword_type: Literal["메인", "세부", "구매의도", "제외"]
    competitors: list[Competitor] = []
    snapshot_date: str
    domain: MarketDomain
