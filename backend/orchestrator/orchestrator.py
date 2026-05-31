import uuid
from datetime import date, datetime, timedelta, timezone
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
        context["coupang_ad_summary"]    = store.get_latest_coupang_ad_summary()
        context["coupang_strategy_mode"] = _get_coupang_strategy_mode(
            context.get("coupang_products", []),
            context["coupang_ad_summary"],
        )
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

        # 운영자 지정 베리 분류 주입 — AI가 이름으로 추론하지 않도록 명시적 주입
        label_map = store.get_product_label_map()
        for p in context.get("collected_products", []):
            p["berry_type"] = label_map.get(p["product_id"])
        for p in context.get("coupang_products", []):
            p["berry_type"] = label_map.get(p["product_id"])

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

        measured = 0
        for log in logs:
            agent       = log["agent"]
            target_id   = log["target_id"]
            action_type = log.get("action_type", "")
            baseline    = log.get("baseline_metrics") or {}

            # 실행 후 7일 윈도우 (executed_at+1 ~ executed_at+7)
            executed_date = log["executed_at"][:10]
            from_date = date.fromisoformat(executed_date) + timedelta(days=1)
            to_date   = date.fromisoformat(executed_date) + timedelta(days=7)

            result: dict = {}
            try:
                if agent == "product_analyzer":
                    from clients import naver_commerce
                    stats = naver_commerce.get_product_order_stats_range(from_date, to_date)
                    s = stats.get(target_id, {})
                    result = {
                        "sales_count_7d": s.get("order_count", 0),
                        "revenue_7d":     s.get("revenue", 0),
                    }

                elif agent == "coupang_analyzer":
                    from clients import coupang
                    orders = coupang.get_revenue_history_range(from_date, to_date)
                    count, revenue = _aggregate_coupang_for_product(orders, target_id)
                    result = {"sales_count_7d": count, "revenue_7d": revenue}

                elif agent == "ad_analyzer":
                    from clients import naver_ad
                    start = from_date.strftime("%Y-%m-%d")
                    end   = to_date.strftime("%Y-%m-%d")

                    if action_type in ("입찰가_조정", "키워드_제외"):
                        keyword_id = baseline.get("target_keyword_id")
                        if keyword_id:
                            raw = naver_ad.get_keyword_stats([keyword_id], start, end)
                            result = _sum_ad_stats(raw, keyword_id)
                    else:
                        campaign_id = baseline.get("target_campaign_id", target_id)
                        raw = naver_ad.get_campaign_stats([campaign_id], start, end)
                        result = _sum_ad_stats(raw, campaign_id)

            except Exception:
                result = {}

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


def _get_coupang_strategy_mode(coupang_products: list[dict], wing_data: list[dict]) -> str:
    total_sales = sum(p.get("sales_count", 0) for p in coupang_products)
    if total_sales == 0:
        base = "READY_CHECK"
    elif total_sales < 10:
        base = "TEST"
    else:
        base = "SCALE"

    # DEFEND: 광고비·클릭 있는데 14일 전환 0 → 클릭 유입이 전환으로 이어지지 않는 상태
    if base != "READY_CHECK" and wing_data:
        defend = any(
            r.get("ad_cost", 0) > 0
            and r.get("clicks", 0) > 0
            and r.get("orders_14d", 0) == 0
            for r in wing_data
        )
        if defend:
            return "DEFEND"

    return base


def _calculate_verdict(baseline: dict, result: dict, agent: str) -> str:
    """7일 전/후 지표를 비교해 판정. 같은 7일 창끼리 비교하므로 희석 없음."""
    if not baseline or not result:
        return "unmeasurable"

    if agent in ("product_analyzer", "coupang_analyzer"):
        b = baseline.get("sales_count_7d")
        r = result.get("sales_count_7d")
    elif agent == "ad_analyzer":
        b = baseline.get("clicks_7d")
        r = result.get("clicks_7d")
    else:
        return "unmeasurable"

    if b is None or r is None or b == 0:
        return "unmeasurable"

    change = (r - b) / b
    if change > 0.05:
        return "positive"
    if change < -0.05:
        return "negative"
    return "neutral"


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
    totals = {"clkCnt": 0, "impCnt": 0, "salesAmt": 0.0}
    for row in raw:
        if str(row.get("id", "")) == entity_id:
            totals["clkCnt"]   += int(float(row.get("clkCnt", 0)))
            totals["impCnt"]   += int(float(row.get("impCnt", 0)))
            totals["salesAmt"] += float(row.get("salesAmt", 0))
    imp, clk = totals["impCnt"], totals["clkCnt"]
    return {
        "clicks_7d":      clk,
        "impressions_7d": imp,
        "ctr_7d":         round(clk / imp, 4) if imp > 0 else 0.0,
    }


orchestrator = Orchestrator()
