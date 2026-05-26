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
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


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
    baseline = store.get_baseline_metrics(row["agent"], row["target_id"], row["target_name"])
    from domain.seasonality import get_season_context
    from orchestrator.orchestrator import _get_strategy_mode
    ad_strategy_mode = _get_strategy_mode(get_season_context()["season_flag"])
    log = await execute(suggestion, baseline_metrics=baseline or None, ad_strategy_mode=ad_strategy_mode)
    return {"suggestion": row, "action_log": log}


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
