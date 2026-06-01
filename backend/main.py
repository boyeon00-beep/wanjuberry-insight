from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import store
from agents.executor.executor import execute
from orchestrator.orchestrator import orchestrator
from routers import coupang_ads

app = FastAPI(title="완주베리 AI 운영 인사이트")

# AI 자동 실행 토글 — false 시 ai_auto 제안도 운영자 직접 완료로 처리
# 나중에 AI 실행을 다시 켜려면 Railway 환경변수 AI_EXECUTION_ENABLED=true 로 변경
AI_EXECUTION_ENABLED = os.environ.get("AI_EXECUTION_ENABLED", "true").lower() == "true"

_cors_origins = os.getenv("CORS_ORIGIN", "*")
cors_origins = [o.strip() for o in _cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coupang_ads.router)


@app.middleware("http")
async def verify_api_token(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    expected = os.getenv("API_TOKEN", "")
    if expected and request.headers.get("X-API-Token", "") != expected:
        origin = request.headers.get("origin", "*")
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized"},
            headers={"Access-Control-Allow-Origin": origin},
        )
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config")
def get_config():
    return {"ai_execution_enabled": AI_EXECUTION_ENABLED}


# --- 분석 실행 ---

@app.post("/analysis/run")
async def run_analysis():
    return await orchestrator.run_analysis()


@app.get("/analysis/runs")
def get_runs():
    return orchestrator.get_runs()


# --- 제안함 ---

@app.get("/suggestions")
def get_suggestions(status: str | None = None):
    return store.get_suggestions(status)


@app.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: str):
    from models.suggestion import Suggestion
    row = store.get_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="제안을 찾을 수 없습니다")
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"이미 처리된 제안입니다: {row['status']}")

    store.update_suggestion_status(suggestion_id, "approved")
    suggestion = Suggestion(**row)
    baseline = _fetch_baseline(row["agent"], row["action_type"], row["target_id"], row["target_name"])

    # AI 자동 실행 비활성화 시: ai_auto 제안도 운영자 직접 완료로 기록
    if not AI_EXECUTION_ENABLED and suggestion.execution_tier == "ai_auto":
        from models.action_log import ActionLog
        log = ActionLog(
            suggestion_id=suggestion_id,
            task_id=suggestion.task_id,
            agent=suggestion.agent,
            action_type=suggestion.action_type,
            target_id=suggestion.target_id,
            target_name=suggestion.target_name,
            execution_tier=suggestion.execution_tier,
            status="completed",
            detail="운영자 직접 완료 (AI 자동 실행 비활성화)",
            baseline_metrics=baseline or None,
        )
        store.add_action_log(log)
        return {"suggestion": row, "action_log": log.model_dump()}

    # AI 자동 실행 (AI_EXECUTION_ENABLED=true 일 때)
    from domain.seasonality import get_season_context
    from orchestrator.orchestrator import _get_strategy_mode
    ad_strategy_mode = _get_strategy_mode(get_season_context()["season_flag"])
    log = await execute(suggestion, baseline_metrics=baseline or None, ad_strategy_mode=ad_strategy_mode)
    return {"suggestion": row, "action_log": log}


def _fetch_baseline(agent: str, action_type: str, target_id: str, target_name: str) -> dict:
    """승인 시점의 직전 7일 지표 수집 — 7일 후 성과 비교의 기준선."""
    from datetime import date, timedelta
    today     = date.today()
    from_date = today - timedelta(days=7)

    if agent == "product_analyzer":
        try:
            from clients import naver_commerce
            stats = naver_commerce.get_product_order_stats_range(from_date, today)
            s = stats.get(target_id, {})
            return {
                "sales_count_7d": s.get("order_count", 0),
                "revenue_7d":     s.get("revenue", 0),
                "baseline_from":  from_date.isoformat(),
                "baseline_to":    today.isoformat(),
            }
        except Exception:
            return {}

    if agent == "coupang_analyzer":
        try:
            from clients import coupang
            orders = coupang.get_revenue_history_range(from_date, today)
            count, revenue = _aggregate_coupang_for_product(orders, target_id)
            return {
                "sales_count_7d": count,
                "revenue_7d":     revenue,
                "baseline_from":  from_date.isoformat(),
                "baseline_to":    today.isoformat(),
            }
        except Exception:
            return {}

    if agent == "ad_analyzer":
        try:
            from clients import naver_ad
            start = from_date.strftime("%Y-%m-%d")
            end   = today.strftime("%Y-%m-%d")

            if action_type in ("입찰가_조정", "키워드_제외"):
                keyword_id = target_id if target_id.startswith("nkw-") else None
                if not keyword_id:
                    return {}
                raw = naver_ad.get_keyword_stats([keyword_id], start, end)
                result = _sum_ad_stats(raw, keyword_id)
                result["target_keyword_id"] = keyword_id
            else:
                # 캠페인 레벨: 예산_조정, 예산_증액, 캠페인_일시중지
                raw = naver_ad.get_campaign_stats([target_id], start, end)
                result = _sum_ad_stats(raw, target_id)
                result["target_campaign_id"] = target_id

            result["baseline_from"] = from_date.isoformat()
            result["baseline_to"]   = today.isoformat()
            return result
        except Exception:
            return {}

    return {}


def _aggregate_coupang_for_product(orders: list[dict], product_id: str) -> tuple[int, int]:
    count, revenue = 0, 0
    for order in orders:
        sign = 1 if order.get("saleType", "SALE") == "SALE" else -1
        for item in order.get("items", []):
            if str(item.get("productId", "")) == product_id:
                count   += sign * int(item.get("quantity", 0))
                revenue += sign * int(item.get("saleAmount", 0))
    return max(count, 0), max(revenue, 0)


def _sum_ad_stats(raw: list[dict], entity_id: str) -> dict:
    clk_total = imp_total = cost_total = 0
    sales_total = 0.0
    for row in raw:
        if str(row.get("id", "")) == entity_id:
            clk  = int(float(row.get("clkCnt", 0)))
            cpc  = float(row.get("cpc", 0))
            clk_total   += clk
            imp_total   += int(float(row.get("impCnt", 0)))
            sales_total += float(row.get("salesAmt", 0))
            cost_total  += int(clk * cpc)  # 일별 clicks × avg_cpc = 일별 광고비
    return {
        "clicks_7d":      clk_total,
        "impressions_7d": imp_total,
        "ctr_7d":         round(clk_total / imp_total, 4) if imp_total > 0 else 0.0,
        "cost_7d":        cost_total,
        "roas_7d":        round(sales_total / cost_total, 2) if cost_total > 0 else None,
    }


class RejectBody(BaseModel):
    rejection_tag: str | None = None


@app.post("/suggestions/{suggestion_id}/reject")
def reject_suggestion(suggestion_id: str, body: RejectBody = RejectBody()):
    from models.action_log import ActionLog
    from models.suggestion import Suggestion

    row = store.get_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="제안을 찾을 수 없습니다")
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"이미 처리된 제안입니다: {row['status']}")

    store.update_suggestion_status(suggestion_id, "rejected", rejection_tag=body.rejection_tag)

    detail = f"거절 — {body.rejection_tag}" if body.rejection_tag else "거절"

    suggestion = Suggestion(**row)
    log = ActionLog(
        suggestion_id=suggestion_id,
        task_id=suggestion.task_id,
        agent=suggestion.agent,
        action_type=suggestion.action_type,
        target_id=suggestion.target_id,
        target_name=suggestion.target_name,
        execution_tier=suggestion.execution_tier,
        status="rejected",
        detail=detail,
    )
    store.add_action_log(log)

    return {"suggestion_id": suggestion_id, "status": "rejected", "rejection_tag": body.rejection_tag}


# --- 네이버 상품 ---

@app.get("/products")
def get_naver_products():
    return [p for p in store.get_latest_products() if p.get("platform") != "coupang"]


# --- 상품 분류 라벨 ---

class ProductLabelBody(BaseModel):
    berry_type: str | None = None


@app.get("/product-labels")
def get_product_labels():
    return store.get_product_labels()


@app.put("/product-labels/{product_id}")
def set_product_label(product_id: str, body: ProductLabelBody):
    products = store.get_latest_products() + store.get_latest_coupang_products()
    product = next((p for p in products if p["product_id"] == product_id), None)
    name = product["name"] if product else product_id
    platform = product["platform"] if product else "unknown"
    store.upsert_product_label(product_id, name, platform, body.berry_type)
    return {"ok": True}


# --- 광고 소재 ---

@app.get("/ads")
def get_ads():
    return store.get_latest_ads()


@app.get("/debug/naver-ad")
def debug_naver_ad():
    """Naver Ad API 원본 응답 진단 — 캠페인/소재/통계 수집 구조 확인"""
    import os
    if not os.environ.get("NAVER_AD_CUSTOMER_ID"):
        return {"mode": "mock", "message": "NAVER_AD_CUSTOMER_ID 미설정 — mock 모드로 동작 중"}

    from clients import naver_ad as client
    from datetime import date, timedelta

    today      = date.today()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date   = today.strftime("%Y-%m-%d")

    result: dict = {"mode": "real", "date_range": f"{start_date} ~ {end_date}"}

    try:
        all_campaigns = client.get_campaigns()
        active = [c for c in all_campaigns if c.get("status") in ("ELIGIBLE", "PAUSED")]
        result["campaigns_total"]  = len(all_campaigns)
        result["campaigns_active"] = len(active)
        result["campaign_ids"]     = [c["nccCampaignId"] for c in active[:5]]

        if active:
            cid = active[0]["nccCampaignId"]
            adgroups = client.get_adgroups(cid)
            result["adgroups_in_first_campaign"] = len(adgroups)

            ads_total = 0
            for ag in adgroups[:3]:
                ag_id = ag["nccAdgroupId"]
                ads = client.get_ads(ag_id)
                ads_total += len(ads)
                if ads:
                    result["sample_ad"] = {
                        "keys": list(ads[0].keys()),
                        "headline_raw": ads[0].get("headline", ""),
                        "description_raw": ads[0].get("description", ""),
                        "adAttr": ads[0].get("adAttr"),
                    }
            result["ads_in_first_3_adgroups"] = ads_total

        if active:
            import httpx as _httpx
            from urllib.parse import quote as _quote
            import json as _json
            campaign_ids = [c["nccCampaignId"] for c in active]
            ids_str = ",".join(campaign_ids)
            fields_str = _quote(_json.dumps(["impCnt", "clkCnt", "salesAmt", "ctr", "cpc", "convAmt"], separators=(',', ':')))
            time_range_str = _quote(_json.dumps({"since": start_date, "until": end_date}, separators=(',', ':')))
            query = f"ids={ids_str}&fields={fields_str}&timeRange={time_range_str}"
            from clients.naver_ad import _headers, _BASE
            raw_res = _httpx.get(f"{_BASE}/stats?{query}", headers=_headers("GET", "/stats"), timeout=20)
            raw_body = raw_res.json()
            result["stats_http_status"] = raw_res.status_code
            result["stats_response_keys"] = list(raw_body.keys()) if isinstance(raw_body, dict) else "array"
            result["stats_raw_preview"] = str(raw_body)[:500]
            data = raw_body.get("data", []) if isinstance(raw_body, dict) else raw_body
            result["stats_returned"] = len(data)
            if data:
                result["sample_stat"] = data[0]
    except Exception as e:
        result["error"] = str(e)

    return result


@app.get("/debug/naver-group-products")
def debug_naver_group_products_list():
    """상품 검색에서 groupProductNo 목록 확인"""
    import os
    if not os.environ.get("NAVER_COMMERCE_CLIENT_ID"):
        return {"mode": "mock", "message": "NAVER_COMMERCE_CLIENT_ID 미설정"}

    from clients import naver_commerce as client
    import httpx as _httpx

    try:
        res = _httpx.post(
            "https://api.commerce.naver.com/external/v1/products/search",
            json={"page": 1, "size": 100},
            headers=client._auth_headers(),
            timeout=15,
        )
        contents = res.json().get("contents", [])
        groups = []
        for item in contents:
            gpn = item.get("groupProductNo")
            if gpn:
                groups.append({
                    "groupProductNo": gpn,
                    "originProductNo": item.get("originProductNo"),
                    "item_keys": list(item.keys()),
                    "channelProducts_count": len(item.get("channelProducts", [])),
                })
        return {
            "total_items": len(contents),
            "items_with_groupProductNo": len(groups),
            "groups": groups[:10],
            "first_item_keys": list(contents[0].keys()) if contents else [],
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/debug/naver-group-product/{group_product_no}")
def debug_naver_group_product(group_product_no: str):
    """그룹상품 API 원본 응답 진단 — 응답 필드명 확인용"""
    import os
    if not os.environ.get("NAVER_COMMERCE_CLIENT_ID"):
        return {"mode": "mock", "message": "NAVER_COMMERCE_CLIENT_ID 미설정"}

    from clients import naver_commerce as client
    import httpx as _httpx

    try:
        res = _httpx.get(
            f"https://api.commerce.naver.com/external/v2/standard-group-products/{group_product_no}",
            headers=client._auth_headers(),
            timeout=10,
        )
        return {
            "http_status": res.status_code,
            "response_keys": list(res.json().keys()) if isinstance(res.json(), dict) else "not_dict",
            "raw": res.json(),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/ads/keyword-volume")
def get_keyword_volume():
    return store.get_latest_keyword_volume()


@app.get("/campaigns")
def get_campaigns():
    return store.get_latest_ad_summary()


# --- 쿠팡 ---

@app.get("/coupang/products")
def get_coupang_products():
    return store.get_latest_coupang_products()


# --- 농장 프로필 ---

class FarmProfileBody(BaseModel):
    content: str


@app.get("/farm-profile")
def get_farm_profile():
    return {"content": store.get_farm_profile()}


@app.put("/farm-profile")
def save_farm_profile(body: FarmProfileBody):
    store.save_farm_profile(body.content)
    return {"content": body.content}


# --- 농장 팩트 (Constraints) ---

class ConstraintBody(BaseModel):
    content: str


@app.get("/constraints")
def get_constraints():
    return store.get_constraints()


@app.post("/constraints")
def add_constraint(body: ConstraintBody):
    return store.add_constraint(body.content, source="manual")


@app.delete("/constraints/{constraint_id}")
def delete_constraint(constraint_id: str):
    store.delete_constraint(constraint_id)
    return {"id": constraint_id, "deleted": True}


@app.patch("/constraints/{constraint_id}")
def update_constraint(constraint_id: str, body: ConstraintBody):
    result = store.update_constraint(constraint_id, body.content)
    if not result:
        raise HTTPException(status_code=404, detail="제약 조건을 찾을 수 없습니다")
    return result


# --- 실행 로그 ---

@app.get("/action-logs")
def get_action_logs():
    return store.get_action_logs()


@app.post("/action-logs/{log_id}/verify")
async def verify_action_log(log_id: str):
    from agents.executor.verifier import verify_action_log as _verify
    log = store.get_action_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="로그를 찾을 수 없습니다")
    verify_status = await _verify(log_id)
    store.update_action_log_verify(log_id, verify_status)
    return {"log_id": log_id, "verify_status": verify_status}
