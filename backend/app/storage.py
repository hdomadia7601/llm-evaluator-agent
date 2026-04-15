import json
from collections import Counter
from pathlib import Path
from threading import Lock
from typing import Any

from .schemas import EvaluateResponse, FeedbackRecord


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EVALS_FILE = DATA_DIR / "evaluations.json"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
_LOCK = Lock()


def _ensure_file(path: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def _read_json(path: Path) -> list[dict[str, Any]]:
    _ensure_file(path)
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def _write_json(path: Path, payload: list[dict[str, Any]]) -> None:
    _ensure_file(path)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def save_evaluation(record: EvaluateResponse) -> None:
    with _LOCK:
        rows = _read_json(EVALS_FILE)
        rows.append(record.model_dump(mode="json"))
        _write_json(EVALS_FILE, rows)


def save_feedback(record: FeedbackRecord) -> None:
    with _LOCK:
        feedback_rows = _read_json(FEEDBACK_FILE)
        payload = record.model_dump(mode="json")
        feedback_rows.append(payload)
        _write_json(FEEDBACK_FILE, feedback_rows)

        # Keep evaluation storage enriched with optional user feedback.
        eval_rows = _read_json(EVALS_FILE)
        for row in reversed(eval_rows):
            if (
                row.get("query") == record.query
                and row.get("response_a") == record.response_a
                and row.get("response_b") == record.response_b
            ):
                row["user_feedback"] = record.user_feedback
                break
        _write_json(EVALS_FILE, eval_rows)


def build_analytics() -> dict[str, Any]:
    with _LOCK:
        evals = _read_json(EVALS_FILE)

    total_queries = len(evals)
    query_counter = Counter((row.get("query") or "").strip().lower() for row in evals if row.get("query"))
    most_common_queries = [
        {"query": query, "count": count}
        for query, count in query_counter.most_common(5)
    ]

    winner_distribution = {"A": 0, "B": 0}
    sums = {
        "clarity": {"a": 0.0, "b": 0.0},
        "completeness": {"a": 0.0, "b": 0.0},
        "correctness": {"a": 0.0, "b": 0.0},
    }

    for row in evals:
        ev = row.get("evaluation", {})
        winner = ev.get("winner")
        if winner in winner_distribution:
            winner_distribution[winner] += 1
        for metric_key, metric_name in [
            ("clarity_scores", "clarity"),
            ("completeness_scores", "completeness"),
            ("correctness_scores", "correctness"),
        ]:
            metric = ev.get(metric_key, {})
            try:
                sums[metric_name]["a"] += float(metric.get("a", 0))
                sums[metric_name]["b"] += float(metric.get("b", 0))
            except (TypeError, ValueError):
                continue

    denom = max(total_queries, 1)
    averages = {
        metric: {"a": round(values["a"] / denom, 2), "b": round(values["b"] / denom, 2)}
        for metric, values in sums.items()
    }

    return {
        "total_queries": total_queries,
        "most_common_queries": most_common_queries,
        "average_evaluation_scores": averages,
        "winner_distribution": winner_distribution,
        "win_rate_percentage": {
            "A": round((winner_distribution["A"] / denom) * 100, 2),
            "B": round((winner_distribution["B"] / denom) * 100, 2),
        },
    }


def build_export_payload() -> dict[str, Any]:
    with _LOCK:
        evals = _read_json(EVALS_FILE)

    analytics = build_analytics()
    avg_scores = analytics["average_evaluation_scores"]
    return {
        "total_queries": analytics["total_queries"],
        "avg_clarity": {"A": avg_scores["clarity"]["a"], "B": avg_scores["clarity"]["b"]},
        "avg_completeness": {"A": avg_scores["completeness"]["a"], "B": avg_scores["completeness"]["b"]},
        "avg_correctness": {"A": avg_scores["correctness"]["a"], "B": avg_scores["correctness"]["b"]},
        "win_rate": analytics["win_rate_percentage"],
        "data": evals,
    }
