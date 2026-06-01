from pydantic import BaseModel
from typing import Literal


class ProductDomain(BaseModel):
    product_type: Literal["생과", "냉동", "즙", "가공품"]
    weight_kg: float
    unit_price_per_kg: float
    season_flag: Literal["성수기", "비수기", "전환기"]


class ProductOption(BaseModel):
    name: str
    price_delta: float
    stock: int


class ProductModel(BaseModel):
    product_id: str
    platform: Literal["naver", "coupang"]
    name: str
    price: float
    options: list[ProductOption] = []
    sales_count: int       # 최근 30일 판매 수량
    sales_revenue: int = 0 # 최근 30일 매출액 (원)
    review_count: int
    review_score: float
    category: str
    tags: list[str] = []
    domain: ProductDomain
    collected_at: str
    vendor_item_ids: list[str] = []  # Wing 보고서 매칭용 vendorItemId 목록
    group_product_no: str = ""       # 그룹상품 번호 (없으면 빈 문자열)
    group_product_name: str = ""     # 그룹상품 대표명 (수집 시 API 조회, DB 미저장)
