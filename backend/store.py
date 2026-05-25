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
        .select("target_id, target_name, action_type, proposed_value, reason, status, rejection_tag, created_at")
        .eq("status", "rejected")
        .order("created_at", desc=True)
        .limit(limit)
    )
    if agent:
        q = q.eq("agent", agent)
    return q.execute().data


def get_effect_history(agent: str | None = None, limit: int = 10) -> list[dict]:
    """effect_verdict가 확정된 action_log 이력 — Learning Loop 프롬프트 주입용."""
    q = (
        get_client()
        .table("action_logs")
        .select("action_type, target_name, effect_verdict, baseline_metrics, result_metrics, executed_at, ad_strategy_mode")
        .not_.is_("effect_verdict", "null")
        .neq("effect_verdict", "pending")
        .order("executed_at", desc=True)
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
        .eq("status", "rejected")
        .limit(1)
        .execute()
    )
    return len(res.data) > 0


def update_suggestion_status(
    suggestion_id: str,
    status: SuggestionStatus,
    rejection_tag: str | None = None,
) -> dict | None:
    payload: dict = {"status": status}
    if rejection_tag:
        payload["rejection_tag"] = rejection_tag
    res = (
        get_client()
        .table("suggestions")
        .update(payload)
        .eq("suggestion_id", suggestion_id)
        .execute()
    )
    return res.data[0] if res.data else None


# --- ActionLog ---

def add_action_log(log: ActionLog) -> None:
    get_client().table("action_logs").insert(log.model_dump()).execute()


def get_baseline_metrics(agent: str, target_id: str, target_name: str) -> dict:
    """승인 시점의 핵심 지표 스냅샷."""
    if agent == "product_analyzer":
        res = (
            get_client()
            .table("collected_products")
            .select("sales_count, sales_revenue, review_count, review_score")
            .eq("product_id", target_id)
            .eq("platform", "naver")
            .order("collected_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else {}

    if agent == "coupang_analyzer":
        res = (
            get_client()
            .table("collected_products")
            .select("sales_count, sales_revenue")
            .eq("product_id", target_id)
            .eq("platform", "coupang")
            .order("collected_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else {}

    if agent == "ad_analyzer":
        runs = get_runs()
        if not runs:
            return {}
        latest_task_id = runs[0]["task_id"]
        res = (
            get_client()
            .table("keyword_volume")
            .select("monthly_total, competition, is_bidding")
            .eq("task_id", latest_task_id)
            .eq("keyword", target_name)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else {}

    return {}


def get_approved_logs_pending_measurement(min_days: int = 7) -> list[dict]:
    """effect_verdict='pending'이고 min_days 이상 지난 성공 로그."""
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=min_days)).isoformat()
    res = (
        get_client()
        .table("action_logs")
        .select("*")
        .eq("effect_verdict", "pending")
        .eq("status", "success")
        .lt("executed_at", cutoff)
        .execute()
    )
    return res.data


def update_action_log_effect(log_id: str, verdict: str, result_metrics: dict) -> None:
    from datetime import datetime, timezone
    get_client().table("action_logs").update({
        "effect_verdict":     verdict,
        "effect_measured_at": datetime.now(timezone.utc).isoformat(),
        "result_metrics":     result_metrics,
    }).eq("log_id", log_id).execute()


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
        "ad_summary":   run.get("ad_summary"),
    }
    get_client().table("analysis_runs").upsert(row).execute()


def get_latest_ad_summary() -> list[dict]:
    res = (
        get_client()
        .table("analysis_runs")
        .select("ad_summary")
        .not_.is_("ad_summary", "null")
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )
    if res.data:
        return res.data[0].get("ad_summary") or []
    return []


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
    from datetime import datetime, timezone
    get_client().table("farm_profile").upsert({
        "id":         1,
        "content":    content,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()


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
            "is_bidding":     v.get("is_bidding", False),
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
        "status":           s.status,
        "is_repeat":        s.is_repeat,
        "validator_verdict": s.validator_verdict,
        "created_at":       s.created_at,
        "expires_at":       s.expires_at,
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
        "vendor_item_ids":    p.get("vendor_item_ids", []),
    }


# --- Coupang Ad Reports ---

def get_product_vendor_item_ids(product_id: str) -> list[str]:
    """product_id → vendor_item_ids (최신 수집 기준). executor 가격/재판매 실행용."""
    res = (
        get_client()
        .table("collected_products")
        .select("vendor_item_ids")
        .eq("product_id", product_id)
        .eq("platform", "coupang")
        .order("collected_at", desc=True)
        .limit(1)
        .execute()
    )
    if res.data:
        return res.data[0].get("vendor_item_ids") or []
    return []


def get_vendor_item_id_map() -> dict[str, str]:
    """vendorItemId → product_id 매핑 (쿠팡 최근 수집 기준)."""
    res = (
        get_client()
        .table("collected_products")
        .select("product_id, vendor_item_ids")
        .eq("platform", "coupang")
        .order("collected_at", desc=True)
        .execute()
    )
    mapping: dict[str, str] = {}
    for row in res.data:
        for vid in (row.get("vendor_item_ids") or []):
            if vid and str(vid) not in mapping:
                mapping[str(vid)] = row["product_id"]
    return mapping


def delete_coupang_ad_report(report_from: str, report_to: str) -> None:
    """동일 기간 기존 데이터 삭제 — 재업로드 시 중복 방지."""
    (
        get_client()
        .table("coupang_ad_reports")
        .delete()
        .eq("report_from", report_from)
        .eq("report_to", report_to)
        .execute()
    )


def save_coupang_ad_report(records: list[dict]) -> None:
    if not records:
        return
    get_client().table("coupang_ad_reports").insert(records).execute()


def get_latest_coupang_ad_summary() -> list[dict]:
    """가장 최근 업로드된 광고 데이터 전체 반환."""
    res = (
        get_client()
        .table("coupang_ad_reports")
        .select("*")
        .order("uploaded_at", desc=True)
        .limit(100)
        .execute()
    )
    return res.data


# --- Product Labels ---

def get_product_label_map() -> dict[str, str | None]:
    """product_id → berry_type 딕셔너리 반환 (오케스트레이터 주입용)."""
    res = get_client().table("product_labels").select("product_id, berry_type").execute()
    return {r["product_id"]: r.get("berry_type") for r in res.data}


def get_product_labels() -> list[dict]:
    """설정 UI용 — 최신 수집 상품 목록에 저장된 라벨을 병합해서 반환."""
    label_map = get_product_label_map()

    products = get_latest_products() + get_latest_coupang_products()
    seen: dict[str, dict] = {}
    for p in products:
        pid = p["product_id"]
        if pid not in seen:
            seen[pid] = {
                "product_id":   pid,
                "product_name": p["name"],
                "platform":     p["platform"],
                "berry_type":   label_map.get(pid),
            }

    for pid, berry_type in label_map.items():
        if pid not in seen:
            res = get_client().table("product_labels").select("product_name, platform").eq("product_id", pid).limit(1).execute()
            row = res.data[0] if res.data else {}
            seen[pid] = {
                "product_id":   pid,
                "product_name": row.get("product_name", pid),
                "platform":     row.get("platform", "unknown"),
                "berry_type":   berry_type,
            }

    return sorted(seen.values(), key=lambda x: (x["platform"], x["product_name"]))


def upsert_product_label(product_id: str, product_name: str, platform: str, berry_type: str | None) -> None:
    get_client().table("product_labels").upsert({
        "product_id":   product_id,
        "product_name": product_name,
        "platform":     platform,
        "berry_type":   berry_type,
    }).execute()
