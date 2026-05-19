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
            await self._step(run, "collect", self._collect, context)
            await self._step(run, "analyze", self._analyze, context)
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
        from agents.collector import naver_commerce, naver_ad

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

        return {
            "sources":        ["naver_commerce", "naver_ad"],
            "naver_commerce": naver_result,
            "naver_ad":       ad_result,
        }

    async def _analyze(self, context: dict) -> dict:
        from agents.analyzer import product, ad
        from models.suggestion import Suggestion

        context["ad_rejection_history"] = store.get_recent_rejections(
            agent="ad_analyzer", limit=10
        )

        product_result = await product.analyze(context)
        ad_result      = await ad.analyze(context)

        all_suggestions = (
            product_result.get("suggestions", []) +
            ad_result.get("suggestions", [])
        )
        suggestions = [Suggestion(**s) for s in all_suggestions]

        for s in suggestions:
            if store.check_has_rejection(s.target_id, s.action_type):
                s.is_repeat = True

        store.add_suggestions(suggestions)

        return {
            "product": product_result,
            "ad":      ad_result,
            "total_suggestions": len(suggestions),
            "saved_to_store":    len(suggestions),
        }

    def get_runs(self) -> list[dict]:
        return store.get_runs()


orchestrator = Orchestrator()
