#!/usr/bin/env python3
"""route.py — zero-LLM model routing helper for Ringer manifest authoring.

Merges the latest OpenRouter catalog (prices/context) with the local
scoreboard (~/.ringer/runs.jsonl: executed-check outcomes per model per
task_type) and prints which models to send jobs to. Run it WHILE drafting a
manifest so routing decisions rest on current prices + this user's evidence,
not vibes.

Usage:
  python3 route.py --task-type code-feature --tasks 4
  python3 route.py --task-type code-feature --tasks 4 --max-usd-per-task 0.25
  python3 route.py --task-type code-review --tokens-in 60000 --tokens-out 8000 --json
  python3 route.py --refresh   # force a fresh catalog pull

Output tiers:
  PROVEN      3+ tasks, first-try >= 2/3 on this machine (the promotion ladder)
  PROBATION   some executed-check evidence, below proven bar
  NO EVIDENCE untested here — exploration candidates only (cheap, big ctx)

Cost model: expected_cost = price_task / first_try (a 33% first-try model
costs 3x in tokens AND wall time). Models without evidence show raw price.

Hard rules applied automatically (user directives, see docs/MODEL-NOTES.md):
  - anthropic/* via OpenRouter is BLOCKED (user pays for Claude directly;
    routing it through OpenRouter would double-bill).
  - Local servers (vllm, local-llama, local-llama-macbookair): $0, offline,
    but at most ONE job per server in flight.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import ringer

DEFAULT_TOKENS_IN = 28_000
DEFAULT_TOKENS_OUT = 12_000
MIN_CTX_FOR_EXPLORATION = 200_000
LOCAL_PREFIXES = ("vllm/", "local-llama", "local-llama-macbookair")


def load_catalog(args: argparse.Namespace) -> list[dict]:
    path = ringer.default_catalog_path()
    need_refresh = args.refresh or not path.exists()
    if not need_refresh:
        try:
            data = json.loads(path.read_text())
            fetched_at = data.get("fetched_at", "")
        except (json.JSONDecodeError, OSError):
            fetched_at = ""
        age_hours = 0.0
        if fetched_at:
            try:
                fetched_ts = time.time() - time.mktime(time.strptime(fetched_at[:19], "%Y-%m-%dT%H:%M:%S"))
                age_hours = max(0.0, fetched_ts / 3600.0)
            except ValueError:
                age_hours = 99.0
        if age_hours > args.stale_hours:
            need_refresh = True
    if need_refresh:
        result = ringer.refresh_openrouter_catalog(path)
        return result.models
    return ringer.load_catalog_snapshot(path)


def load_scoreboard(task_type: str | None) -> dict[str, dict]:
    rows, _ = ringer.read_model_log_rows(ringer.ringer_home() / "runs.jsonl")
    groups = ringer.aggregate_model_log_rows(rows, task_type=task_type)
    out: dict[str, dict] = {}
    for g in groups:
        model = g.get("model") or ""
        if not model:
            continue
        prev = out.get(model)
        # task_type=None means "all types": keep the group with the most tasks
        if prev is None or g.get("tasks", 0) > prev.get("tasks", 0):
            out[model] = g
    return out


def is_local(slug: str) -> bool:
    return slug.startswith(LOCAL_PREFIXES)


def price_per_task(model: dict, tokens_in: int, tokens_out: int) -> float | None:
    if model.get("variable_pricing") or model.get("free"):
        return 0.0
    pin = float(model.get("prompt_per_m") or 0)
    pout = float(model.get("completion_per_m") or 0)
    return tokens_in / 1e6 * pin + tokens_out / 1e6 * pout


def match_evidence(evidence: dict[str, dict], catalog_id: str) -> dict | None:
    for slug in (f"openrouter/{catalog_id}", catalog_id):
        if slug in evidence:
            return evidence[slug]
    return None


def fmt_price(x: float | None) -> str:
    if x is None:
        return "?"
    if x == 0:
        return "0.00"
    if x < 0.01:
        return f"{x:.4f}"
    return f"{x:.3f}"


def fmt_min(ms: int | None) -> str:
    if not ms:
        return "?"
    return f"{ms / 60000:.1f}m"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task-type", default=None, help="scoreboard task_type filter (code-feature, code, ...)")
    ap.add_argument("--tasks", type=int, default=0, help="propose an assignment for N tasks")
    ap.add_argument("--tokens-in", type=int, default=DEFAULT_TOKENS_IN)
    ap.add_argument("--tokens-out", type=int, default=DEFAULT_TOKENS_OUT)
    ap.add_argument("--max-usd-per-task", type=float, default=0.5, help="cap for no-evidence exploration candidates")
    ap.add_argument("--stale-hours", type=float, default=24.0)
    ap.add_argument("--refresh", action="store_true", help="force a fresh catalog pull")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    catalog = load_catalog(args)
    evidence = load_scoreboard(args.task_type)
    # Cross-evidence: a model proven on OTHER task types is still a smarter
    # pick than an untested one — surface it when the filtered slice is thin.
    evidence_all = load_scoreboard(None) if args.task_type else evidence

    proven, probation, no_evidence, local_rows = [], [], [], []
    for model in catalog:
        mid = model.get("id", "")
        if not mid or mid.startswith("anthropic/"):
            continue  # hard block: OpenRouter Claude (user directive)
        price = price_per_task(model, args.tokens_in, args.tokens_out)
        ctx = int(model.get("context_length") or 0)
        ev = match_evidence(evidence, mid)
        cross = match_evidence(evidence_all, mid) if args.task_type else None
        row = {
            "model": f"openrouter/{mid}",
            "ctx": ctx,
            "free": bool(model.get("free")),
            "price_task": price,
            "evidence": None,
        }
        if ev:
            ft = float(ev.get("first_try_pass_rate") or 0)
            row["evidence"] = {
                "tasks": ev.get("tasks", 0),
                "first_try": ft,
                "pass": ev.get("pass_rate", 0.0),
                "median_tokens": ev.get("median_tokens"),
                "median_min": (ev.get("median_duration_ms") or 0) / 60000,
            }
            if ft > 0:
                row["expected_cost"] = price / ft
                row["expected_min"] = row["evidence"]["median_min"] / ft
            else:
                row["expected_cost"] = price
                row["expected_min"] = row["evidence"]["median_min"]
            tier = ringer.model_scoreboard_tier(ev.get("tasks", 0), ft)
            if tier != "proven" and cross and cross.get("tasks", 0) > ev.get("tasks", 0):
                cft = float(cross.get("first_try_pass_rate") or 0)
                row["cross"] = (
                    f"all-types: {cross.get('tasks', 0)}t {cft:.0%}ft"
                    + (" (PROVEN)" if ringer.model_scoreboard_tier(cross.get("tasks", 0), cft) == "proven" else "")
                )
            (proven if tier == "proven" else probation).append(row)
        else:
            row["expected_cost"] = price
            row["expected_min"] = None
            if ctx >= MIN_CTX_FOR_EXPLORATION and price is not None and price <= args.max_usd_per_task:
                no_evidence.append(row)

    # local servers: from the scoreboard (they have no catalog entries)
    for slug, g in evidence.items():
        if not is_local(slug):
            continue
        ft = float(g.get("first_try_pass_rate") or 0)
        local_rows.append(
            {
                "model": slug,
                "price_task": 0.0,
                "evidence": {
                    "tasks": g.get("tasks", 0),
                    "first_try": ft,
                    "pass": g.get("pass_rate", 0.0),
                    "median_min": (g.get("median_duration_ms") or 0) / 60000,
                },
                "expected_min": (g.get("median_duration_ms") or 0) / 60000 / ft if ft > 0 else None,
                "note": "local server: max 1 job in flight",
            }
        )

    proven.sort(key=lambda r: (r["expected_cost"] if r["expected_cost"] is not None else 1e9))
    probation.sort(key=lambda r: (r["expected_cost"] if r["expected_cost"] is not None else 1e9))
    no_evidence.sort(key=lambda r: (r["price_task"] or 0))

    if args.json:
        print(
            json.dumps(
                {
                    "task_type": args.task_type,
                    "tokens_in": args.tokens_in,
                    "tokens_out": args.tokens_out,
                    "proven": proven,
                    "probation": probation,
                    "no_evidence": no_evidence[:10],
                    "local": local_rows,
                },
                indent=2,
            )
        )
        return 0

    def show(rows: list[dict]) -> None:
        for r in rows:
            ev = r["evidence"]
            ev_s = (
                f"{ev['tasks']}t {ev['first_try']:.0%}ft"
                if ev
                else "no evidence"
            )
            extra = "FREE" if r.get("free") else ""
            cross_s = f"  [{r['cross']}]" if r.get("cross") else ""
            print(
                f"  {r['model']:<44} {fmt_price(r['price_task']):>8}/task  "
                f"ctx {r.get('ctx', 0) // 1000:>5}k  {ev_s:<16} exp {fmt_price(r.get('expected_cost')):>8}  {fmt_min((r.get('expected_min') or 0) * 60000 if r.get('expected_min') else None):>6}  {extra}{cross_s}"
            )

    tt = args.task_type or "(all task types)"
    print(f"route: task_type={tt}  tokens≈{(args.tokens_in + args.tokens_out) // 1000}k  (catalog + local scoreboard, zero LLM)\n")
    print("PROVEN (3+ tasks, first-try ≥ 67%) — safe to assign bulk lanes:")
    show(proven) if proven else print("  (none)")
    print("\nPROBATION (some evidence):")
    show(probation) if probation else print("  (none)")
    print(f"\nNO EVIDENCE (exploration candidates, ≤{args.max_usd_per_task}$/task, ctx ≥ {MIN_CTX_FOR_EXPLORATION // 1000}k) — at most ONE per run:")
    show(no_evidence[:10]) if no_evidence else print("  (none)")
    print("\nLOCAL (free/offline, max 1 job per server in flight):")
    show(local_rows) if local_rows else print("  (none)")

    if args.tasks:
        n = args.tasks
        cross_proven = [r for r in probation if r.get("cross") and "(PROVEN)" in r["cross"]]
        pool = proven or cross_proven or probation
        print(f"\nSUGGESTED ASSIGNMENT for {n} task(s):")
        if not pool:
            print("  no evidence yet — send 1 task to the cheapest no-evidence model, rest to local 27B")
            if no_evidence:
                print(f"  1x {no_evidence[0]['model']} (exploration) + {n - 1}x local (vllm/qwen3.8-27b)")
        else:
            primary = pool[0]
            explore = no_evidence[0] if (n >= 3 and no_evidence) else None
            print(f"  {n - (1 if explore else 0)}x {primary['model']}  (proven/probation, cheapest expected)")
            if explore:
                print(f"  1x {explore['model']}  (exploration slot, ~{fmt_price(explore['price_task'])}/task)")
        print("  max_parallel = 1 per local server; cloud lanes may run in parallel")

    return 0


if __name__ == "__main__":
    sys.exit(main())
