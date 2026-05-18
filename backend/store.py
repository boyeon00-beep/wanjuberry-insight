from db.supabase_client import get_client
from models.action_log import ActionLog
from models.suggestion import Suggestion, SuggestionStatus


# --- Suggestion ---

def add_suggestions(items: list[Suggestion]) -> None:
    if not items:
        return
    rows = [_suggestion_to_row(s) for s in items]
    get_client().table("suggestions").insert(rows).execute()


def get_suggestions(status: SuggestionStatus | None = None) -> list[dict]:
    q = get_client().table("suggestions").select("*").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    res = q.execute()
    return res.data


def get_suggestion(suggestion_id: str) -> dict | None:
    res = (
        get_client()
        .table("suggestions")
        .select("*")
        .eq("suggestion_id", suggestion_id)
        .maybe_single()
        .execute()
    )
    return res.data


def update_suggestion_status(suggestion_id: str, status: SuggestionStatus) -> dict | None:
    res = (
        get_client()
        .table("suggestions")
        .update({"status": status})
        .eq("suggestion_id", suggestion_id)
        .execute()
    )
    return res.data[0] if res.data else None


# --- ActionLog ---

def add_action_log(log: ActionLog) -> None:
    get_client().table("action_logs").insert(log.model_dump()).execute()


def get_action_logs() -> list[dict]:
    res = (
        get_client()
        .table("action_logs")
        .select("*")
        .order("executed_at", desc=True)
        .execute()
    )
    return res.data


# --- AnalysisRun ---

def save_run(run: dict) -> None:
    row = {
        "task_id":      run["task_id"],
        "started_at":   run["started_at"],
        "completed_at": run.get("completed_at"),
        "season_flag":  run["season_flag"],
        "season_note":  run.get("season_note"),
        "status":       run["status"],
        "error":        run.get("error"),
    }
    get_client().table("analysis_runs").upsert(row).execute()


def get_runs() -> list[dict]:
    res = (
        get_client()
        .table("analysis_runs")
        .select("*")
        .order("started_at", desc=True)
        .execute()
    )
    return res.data


# --- CollectedProducts ---

def save_products(task_id: str, products: list[dict]) -> None:
    if not products:
        return
    rows = [_product_to_row(task_id, p) for p in products]
    get_client().table("collected_products").insert(rows).execute()


def get_latest_products() -> list[dict]:
    # 가장 최근 run의 상품만 반환
    runs = get_runs()
    if not runs:
        return []
    latest_task_id = runs[0]["task_id"]
    res = (
        get_client()
        .table("collected_products")
        .select("*")
        .eq("task_id", latest_task_id)
        .execute()
    )
    return res.data


# --- 내부 변환 ---

def _suggestion_to_row(s: Suggestion) -> dict:
    return {
        "suggestion_id":  s.suggestion_id,
        "task_id":        s.task_id,
        "agent":          s.agent,
        "target_id":      s.target_id,
        "target_name":    s.target_name,
        "action_type":    s.action_type,
        "current_value":  s.current_value,
        "proposed_value": s.proposed_value,
        "reason":         s.reason,
        "priority":       s.priority,
        "execution_tier": s.execution_tier,
        "status":         s.status,
        "created_at":     s.created_at,
        "expires_at":     s.expires_at,
    }


def _product_to_row(task_id: str, p: dict) -> dict:
    return {
        "task_id":            task_id,
        "product_id":         p["product_id"],
        "platform":           p["platform"],
        "name":               p["name"],
        "price":              p["price"],
        "sales_count":        p["sales_count"],
        "review_count":       p["review_count"],
        "review_score":       p["review_score"],
        "category":           p.get("category"),
        "tags":               p.get("tags", []),
        "sales_revenue":      p.get("sales_revenue", 0),
        "product_type":       p["domain"]["product_type"],
        "weight_kg":          p["domain"]["weight_kg"],
        "unit_price_per_kg":  p["domain"]["unit_price_per_kg"],
        "season_flag":        p["domain"]["season_flag"],
        "options":            p.get("options", []),
        "collected_at":       p["collected_at"],
    }
