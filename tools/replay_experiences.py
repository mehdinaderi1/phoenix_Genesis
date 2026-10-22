import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import json

"""
Replay experiences from historical sessions.

Extracts closed trades from data/paper_sessions/*.json and populates:
- data/memory/experiences.jsonl          (trade outcomes)
- data/memory/strategy_performance.jsonl (per-strategy pnl)
- data/memory/meta_feedback.jsonl        (synthesized meta signals)

Idempotent via manifest: re-running will skip already-processed sessions.

Usage:
    python tools/replay_experiences.py --dry-run
    python tools/replay_experiences.py
    python tools/replay_experiences.py --force    # ignore manifest
"""
import json
import sys
from pathlib import Path

ROOT = _project_root / "data" / "paper_sessions"
ORPHANED = ROOT / "_orphaned"
MANIFEST = _project_root / "data" / "memory" / "_replay_manifest.json"


def load_manifest():
    if MANIFEST.exists():
        try:
            return set(json.loads(MANIFEST.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def save_manifest(ids):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(sorted(ids), ensure_ascii=False),
        encoding="utf-8",
    )


def iter_sessions():
    for d in (ROOT, ORPHANED):
        if not d.exists():
            continue
        for path in sorted(d.glob("*.json")):
            if path.name.endswith(".checkpoint.json"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"  SKIP {path.name}: {exc}")
                continue
            yield path, data


def _compute_strategy(entry):
    regime = entry.get("regime")
    signal = entry.get("signal")
    risk = entry.get("risk")
    if regime is None and signal is None and risk is None:
        return "RECOVERY"
    return (
        f"{regime or 'UNKNOWN'}_"
        f"{signal or 'WAIT'}_"
        f"{risk or 'UNKNOWN'}"
    )


def extract_trades(session_data):
    """Yield (entry_cycle, close_cycle, is_partial) for every realized event."""
    stack = []
    for cycle in session_data.get("cycles", []):
        action = cycle.get("action")

        if action == "OPEN":
            stack.append(cycle)

        elif action in ("CLOSE", "RECOVERY_CLOSE"):
            if stack:
                entry = stack.pop()
            else:
                # pre-session position; use the close cycle as surrogate entry
                entry = cycle
            yield (entry, cycle, False)

        elif action == "PARTIAL" and stack:
            yield (stack[-1], cycle, True)


def make_records(entry, close, partial):
    pnl = close.get("realized_pnl") or 0.0
    if pnl == 0.0:
        return None  # no signal

    regime = entry.get("regime") or "UNKNOWN"
    signal = entry.get("signal") or "WAIT"
    risk = entry.get("risk") or "UNKNOWN"
    confidence = entry.get("confidence")
    if confidence is None:
        confidence = 50.0

    strategy = _compute_strategy(entry)
    success = pnl > 0.0
    score = round(pnl * 100.0, 4)

    return {
        "experience": {
            "regime": regime,
            "signal": signal,
            "risk": risk,
            "success": success,
            "score": score,
            "strategy": strategy,
            "champion_strategy": strategy,
            "confidence": confidence,
            "trace": {
                "source": "replay",
                "partial": partial,
                "cycle_close": close.get("cycle"),
            },
        },
        "performance": {
            "strategy": strategy,
            "profit_loss": pnl,
            "success": success,
        },
        "meta_feedback": {
            "confidence_before": 50.0,
            "adjustment": 0.0,
            "confidence_after": 50.0,
            "outcome": "SUCCESS" if success else "FAILURE",
            "meta_effective": success,
        },
    }


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    manifest = load_manifest() if not force else set()

    experiences = []
    performances = []
    meta_feedbacks = []
    processed_ids = set()
    trades_per_session = {}

    print(f"{'session':38} {'where':10} {'trades':>7}")
    print("-" * 60)

    for path, data in iter_sessions():
        sid = data.get("session_id") or path.stem
        if sid in manifest:
            continue

        where = "_orphaned" if path.parent.name == "_orphaned" else "root"
        count = 0

        for entry, close, partial in extract_trades(data):
            recs = make_records(entry, close, partial)
            if recs is None:
                continue
            experiences.append(recs["experience"])
            performances.append(recs["performance"])
            meta_feedbacks.append(recs["meta_feedback"])
            count += 1

        if count:
            trades_per_session[sid] = count
            processed_ids.add(sid)
            print(f"{sid:38} {where:10} {count:>7}")

    print("-" * 60)
    print(f"Sessions with trades:     {len(trades_per_session)}")
    print(f"New experiences:          {len(experiences)}")
    print(f"New performances:         {len(performances)}")
    print(f"New meta_feedbacks:       {len(meta_feedbacks)}")

    wins = sum(1 for e in experiences if e["success"])
    losses = len(experiences) - wins
    print(f"Wins: {wins}  |  Losses: {losses}")

    # strategy breakdown (correct per-record pnl via zip)
    by_strategy = {}
    for exp, perf in zip(experiences, performances):
        s = exp["strategy"]
        if s not in by_strategy:
            by_strategy[s] = {"n": 0, "pnl": 0.0, "wins": 0}
        by_strategy[s]["n"] += 1
        by_strategy[s]["pnl"] += perf["profit_loss"]
        if exp["success"]:
            by_strategy[s]["wins"] += 1

    print("\nBy strategy:")
    for s, info in sorted(by_strategy.items()):
        wr = info["wins"] / info["n"] * 100 if info["n"] else 0
        print(
            f"  {s:50} n={info['n']:>2}  "
            f"pnl={info['pnl']:+.4f}  win={wr:>3.0f}%"
        )

    if dry_run:
        print("\n[DRY-RUN] no files written")
        return

    if not experiences:
        print("\nNothing to write.")
        return

    from intelligence.memory._persistence import append_record

    from intelligence.memory._persistence import append_record

    exp_path = _project_root / "data" / "memory" / "experiences.jsonl"
    perf_path = _project_root / "data" / "memory" / "strategy_performance.jsonl"
    meta_path = _project_root / "data" / "memory" / "meta_feedback.jsonl"

    for exp in experiences:
        append_record(exp_path, exp)
    for perf in performances:
        append_record(perf_path, perf)
    for meta in meta_feedbacks:
        append_record(meta_path, meta)

    save_manifest(manifest | processed_ids)

    print(f"\nWrote:")
    print(f"  data/memory/experiences.jsonl          +{len(experiences)}")
    print(f"  data/memory/strategy_performance.jsonl +{len(performances)}")
    print(f"  data/memory/meta_feedback.jsonl        +{len(meta_feedbacks)}")
    print(f"  manifest: {len(manifest | processed_ids)} sessions")


if __name__ == "__main__":
    main()