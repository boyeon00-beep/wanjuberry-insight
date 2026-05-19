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


def get_recent_rejections(agent: str | None = None, limit: int = 10) -> list[dict]:
    q = (
        get_client()
        .table("suggestions")
        .select("target_id, target_name, action_type, proposed_value, reason, status, created_at")
        .in_("status", ["rejected", "expired"])
        .order("created_at", desc=True)
        .limit(limit)
    )
    if agent:
        q = q.eq("agent", agent)
    return q.execute().data


def check_has_rejection(target_id: str, action_type: str) -> bool:
    res = (
        get_client()
        .table("suggestions")
        .select("suggestion_id")
        .eq("target_id", target_id)
        .eq("action_type", action_type)
        .in_("status", ["rejected", "expired"])
        .limit(1)
        .execute()
    )
    return len(res.data) > 0


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


def get_latest_coupang_products() -> list[dict]:
    runs = get_runs()
    if not runs:
        return []
    latest_task_id = runs[0]["task_id"]
    res = (
        get_client()
        .table("collected_products")
        .select("*")
        .eq("task_id", latest_task_id)
        .eq("platform", "coupang")
        .execute()
    )
    return res.data


# --- CollectedAds ---

def save_ads(task_id: str, ad_copies: list[dict]) -> None:
    if not ad_copies:
        return
    rows = [_ad_copy_to_row(task_id, c) for c in ad_copies]
    get_client().table("collected_ads").insert(rows).execute()


def get_latest_ads() -> list[dict]:
    runs = get_runs()
    if not runs:
        return []
    latest_task_id = runs[0]["task_id"]
    res = (
        get_client()
        .table("collected_ads")
        .select("*")
        .eq("task_id", latest_task_id)
        .execute()
    )
    return res.data


# --- FarmProfile ---

def get_farm_profile() -> str:
    res = get_client().table("farm_profile").select("content").eq("id", 1).maybe_single().execute()
    return res.data["content"] if res.data else ""


def save_farm_profile(content: str) -> None:
    get_client().table("farm_profile").upsert({"id": 1, "content": content, "updated_at": "now()"}).execute()


# --- KeywordVolume ---

def save_keyword_volume(task_id: str, volumes: list[dict]) -> None:
    if not volumes:
        return
    rows = [
        {
            "task_id":        task_id,
            "keyword":        v["keyword"],
            "monthly_pc":     v["monthly_pc"],
            "monthly_mobile": v["monthly_mobile"],
            "monthly_total":  v["monthly_total"],
            "competition":    v["competition"],
            "is_bidding":     v["is_bidding"],
        }
        for v in volumes
        if v.get("keyword")
    ]
    get_client().table("keyword_volume").insert(rows).execute()


def get_latest_keyword_volume() -> list[dict]:
    runs = get_runs()
    if not runs:
        return []
    latest_task_id = runs[0]["task_id"]
    res = (
        get_client()
        .table("keyword_volume")
        .select("*")
        .eq("task_id", latest_task_id)
        .order("monthly_total", desc=True)
        .execute()
    )
    return res.data


# --- Constraints (농장 팩트) ---

def get_constraints() -> list[dict]:
    res = get_client().table("constraints").select("*").order("created_at", desc=True).execute()
    return res.data


def add_constraint(content: str, source: str = "manual") -> dict:
    res = get_client().table("constraints").insert({"content": content, "source": source}).execute()
    return res.data[0]


def delete_constraint(constraint_id: str) -> None:
    get_client().table("constraints").delete().eq("id", constraint_id).execute()


def update_constraint(constraint_id: str, content: str) -> dict | None:
    res = (
        get_client()
        .table("constraints")
        .update({"content": content})
        .eq("id", constraint_id)
        .execute()
    )
    return res.data[0] if res.data else None


def expire_pending_suggestions() -> int:
    res = (
        get_client()
        .table("suggestions")
        .update({"status": "expired"})
        .eq("status", "pending")
        .execute()
    )
    return len(res.data)


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
        "is_repeat":      s.is_repeat,
        "created_at":     s.created_at,
        "expires_at":     s.expires_at,
    }


def _ad_copy_to_row(task_id: str, c: dict) -> dict:
    return {
        "task_id":      task_id,
        "ad_id":        c["ad_id"],
        "adgroup_id":   c["adgroup_id"],
        "campaign_id":  c["campaign_id"],
        "headline":     c["headline"],
        "description1": c["description1"],
        "description2": c.get("description2", ""),
        "ad_type":      c.get("ad_type", ""),
        "status":       c.get("status", ""),
        "collected_at": c.get("collected_at"),
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
