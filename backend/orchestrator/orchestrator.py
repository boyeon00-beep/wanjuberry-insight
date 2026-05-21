import uuid
from datetime import datetime, timezone
from typing import Literal

import store
from domain.seasonality import get_season_context

TaskStatus = Literal["running", "success", "error"]


class Orchestrator:
    async def run_analysis(self) -> dict:
        task_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()

        season = get_season_context()
        context = {
            "task_id":     task_id,
            "season_flag": season["season_flag"],
            "season_note": season["note"],
            "triggered_by": "user",
        }

        run = {
            "task_id":     task_id,
            "started_at":  started_at,
            "season_flag": season["season_flag"],
            "season_note": season["note"],
            "steps":       [],
            "status":      "running",
        }

        store.save_run(run)

        try:
            await self._step(run, "collect",          self._collect,          context)
            # 광고 캠페인 데이터 저장 (수집 직후 run에 추가)
            _cs = next((s for s in run["steps"] if s["name"] == "collect"), None)
            if _cs and _cs.get("status") == "success":
                run["ad_summary"] = _cs.get("result", {}).get("naver_ad", {}).get("campaigns", [])
            await self._step(run, "measure_effects",  self._measure_effects,  context)
            await self._step(run, "analyze",          self._analyze,          context)
            run["status"] = "success"
        except Exception as e:
            run["status"] = "error"
            run["error"] = str(e)

        run["completed_at"] = datetime.now(timezone.utc).isoformat()
        store.save_run(run)
        return run

    async def _step(self, run: dict, name: str, fn, context: dict):
        step = {"name": name, "status": "running"}
        run["steps"].append(step)
        try:
            result = await fn(context)
            step["status"] = "success"
            step["result"] = result
        except NotImplementedError:
            step["status"] = "not_implemented"
        except Exception as e:
            step["status"] = "error"
            step["error"] = str(e)
            raise

    async def _collect(self, context: dict) -> dict:
        from agents.collector import naver_commerce, naver_ad, coupang

        naver_result = await naver_commerce.collect(context)
        products = naver_result.get("products", [])
        context["collected_products"] = products
        store.save_products(context["task_id"], products)

        ad_result = await naver_ad.collect(context)
        context["collected_campaigns"] = ad_result.get("campaigns", [])

        ad_copies = ad_result.get("ad_copies", [])
        if ad_copies:
            store.save_ads(context["task_id"], ad_copies)
        context["collected_ad_copies"] = ad_copies
        kw_volume = ad_result.get("keyword_volume", [])
        context["keyword_volume"] = kw_volume
        if kw_volume:
            store.save_keyword_volume(context["task_id"], kw_volume)

        coupang_result   = await coupang.collect(context)
        coupang_products = coupang_result.get("products", [])
        context["coupang_products"] = coupang_products
        if coupang_products:
            store.save_products(context["task_id"], coupang_products)

        return {
            "sources":        ["naver_commerce", "naver_ad", "coupang"],
            "naver_commerce": naver_result,
            "naver_ad":       ad_result,
            "coupang":        coupang_result,
        }

    async def _analyze(self, context: dict) -> dict:
        from agents.analyzer import product, ad, coupang as coupang_analyzer
        from models.suggestion import Suggestion

        # 이전 pending 제안 만료 — 새 분석 결과만 유효
        store.expire_pending_suggestions()

        context["farm_profile"]          = store.get_farm_profile()
        context["farm_constraints"]      = store.get_constraints()
        context["ad_strategy_mode"]      = _get_strategy_mode(context["season_flag"])
        context["coupang_strategy_mode"] = _get_coupang_strategy_mode(context.get("coupang_products", []))
        context["ad_rejection_history"] = store.get_recent_rejections(
            agent="ad_analyzer", limit=10
        )
        context["coupang_rejection_history"] = store.get_recent_rejections(
            agent="coupang_analyzer", limit=10
        )
        context["product_rejection_history"] = store.get_recent_rejections(
            agent="product_analyzer", limit=10
        )
        context["ad_effect_history"]      = store.get_effect_history(agent="ad_analyzer",      limit=8)
        context["product_effect_history"] = store.get_effect_history(agent="product_analyzer", limit=8)
        context["coupang_effect_history"] = store.get_effect_history(agent="coupang_analyzer", limit=8)

        product_result  = await product.analyze(context)
        ad_result       = await ad.analyze(context)
        coupang_result  = await coupang_analyzer.analyze(context)

        all_suggestions = (
            product_result.get("suggestions", []) +
            ad_result.get("suggestions", []) +
            coupang_result.get("suggestions", [])
        )
        suggestions = [Suggestion(**s) for s in all_suggestions]

        for s in suggestions:
            if store.check_has_rejection(s.target_id, s.action_type):
                s.is_repeat = True

        # Validator: BLOCK 제외 후 저장
        from agents.validator import validator as _validator
        verdicts = await _validator.validate(
            [s.model_dump() for s in suggestions], context
        )

        final: list[Suggestion] = []
        blocked = 0
        for s in suggestions:
            v = verdicts.get(s.suggestion_id, {"verdict": "PASS", "note": ""})
            verdict = v["verdict"]
            note    = v.get("note", "")
            if verdict == "BLOCK":
                blocked += 1
                continue
            s.validator_verdict = verdict
            if verdict in ("WARN", "NEEDS_DATA") and note:
                s.reason = s.reason + f"\n[검증] {note}"
            final.append(s)

        store.add_suggestions(final)

        return {
            "product": product_result,
            "ad":      ad_result,
            "coupang": coupang_result,
            "total_suggestions":  len(suggestions),
            "blocked_by_validator": blocked,
            "saved_to_store":     len(final),
        }

    async def _measure_effects(self, context: dict) -> dict:
        logs = store.get_approved_logs_pending_measurement(min_days=7)
        if not logs:
            return {"measured": 0}

        product_map = {p["product_id"]: p for p in context.get("collected_products", [])}
        coupang_map = {p["product_id"]: p for p in context.get("coupang_products", [])}
        kw_map      = {k["keyword"]: k   for k in context.get("keyword_volume", [])}

        measured = 0
        for log in logs:
            agent       = log["agent"]
            target_id   = log["target_id"]
            target_name = log["target_name"]
            baseline    = log.get("baseline_metrics") or {}

            result: dict = {}
            if agent == "product_analyzer" and target_id in product_map:
                p = product_map[target_id]
                result = {"sales_count": p.get("sales_count", 0), "sales_revenue": p.get("sales_revenue", 0)}
            elif agent == "coupang_analyzer" and target_id in coupang_map:
                p = coupang_map[target_id]
                result = {"sales_count": p.get("sales_count", 0), "sales_revenue": p.get("sales_revenue", 0)}
            elif agent == "ad_analyzer" and target_name in kw_map:
                k = kw_map[target_name]
                result = {"monthly_total": k.get("monthly_total", 0)}

            verdict = _calculate_verdict(baseline, result, agent)
            store.update_action_log_effect(log["log_id"], verdict, result)
            measured += 1

        return {"measured": measured}

    def get_runs(self) -> list[dict]:
        return store.get_runs()


def _get_strategy_mode(season_flag: str) -> str:
    if season_flag == "성수기":
        return "SCALE"
    if season_flag == "전환기":
        return "TEST"
    return "PREPARE"


def _get_coupang_strategy_mode(coupang_products: list[dict]) -> str:
    total_sales = sum(p.get("sales_count", 0) for p in coupang_products)
    if total_sales == 0:
        return "READY_CHECK"
    if total_sales < 10:
        return "TEST"
    return "SCALE"


def _calculate_verdict(baseline: dict, result: dict, agent: str) -> str:
    if not baseline or not result:
        return "unmeasurable"

    key = "sales_count" if agent in ("product_analyzer", "coupang_analyzer") else "monthly_total"
    b = baseline.get(key)
    r = result.get(key)

    if b is None or r is None or b == 0:
        return "unmeasurable"

    change = (r - b) / b
    if change > 0.05:
        return "positive"
    if change < -0.05:
        return "negative"
    return "neutral"


orchestrator = Orchestrator()
