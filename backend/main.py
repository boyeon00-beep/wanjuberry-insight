from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import store
from agents.executor.executor import execute
from orchestrator.orchestrator import orchestrator

app = FastAPI(title="완주베리 AI 운영 인사이트")

_cors_origins = os.getenv("CORS_ORIGIN", "*")
cors_origins = [o.strip() for o in _cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    log = await execute(suggestion)
    return {"suggestion": row, "action_log": log}


@app.post("/suggestions/{suggestion_id}/reject")
def reject_suggestion(suggestion_id: str):
    row = store.get_suggestion(suggestion_id)
    if not row:
        raise HTTPException(status_code=404, detail="제안을 찾을 수 없습니다")
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"이미 처리된 제안입니다: {row['status']}")

    store.update_suggestion_status(suggestion_id, "rejected")
    return {"suggestion_id": suggestion_id, "status": "rejected"}


# --- 실행 로그 ---

@app.get("/action-logs")
def get_action_logs():
    return store.get_action_logs()
