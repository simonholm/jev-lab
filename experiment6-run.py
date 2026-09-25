"""Apply the frozen Experiment 6 policy to the existing Jev capture offline."""

import hashlib
import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CATEGORIES = {"decision", "implementation", "troubleshooting", "observation", "discussion", "other"}
NOUL_FIELDS = {
    "explicit_decision": "concrete_decision",
    "completed_change": "completed_change",
    "retain_for_history": "project_history",
    "missing_required_context": "needs_context",
}


def rows(name):
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines()]


def sha256(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    freeze = json.loads((ROOT / "experiment6-freeze.json").read_text())
    for name, expected_hash in freeze["files_sha256"].items():
        assert sha256(name) == expected_hash, f"frozen file changed: {name}"
    for name, key in [
        ("experiment5-records.jsonl", "source_records_sha256"),
        ("experiment5-expected.jsonl", "source_labels_sha256"),
        ("experiment5-jev-results.jsonl", "source_jev_capture_sha256"),
    ]:
        assert sha256(name) == freeze[key], f"source changed: {name}"

    records = rows("experiment5-records.jsonl")
    capture = rows("experiment5-jev-results.jsonl")
    assert len(records) == len(capture) == freeze["record_count"] == 61
    route = runpy.run_path(str(ROOT / "experiment6-policy.py"))["route"]
    results = []
    for record, captured in zip(records, capture):
        assert captured["record"] == {"id": record["id"], "text": record["text"]}
        assert "error" not in captured and "http_status" not in captured
        answers = captured["response"]["answers"]
        category_answer = answers["category"]
        category = category_answer["choice"]
        confidence = category_answer["confidence"]
        assert category_answer["type"] == "choice" and category in CATEGORIES
        assert isinstance(confidence, (int, float)) and 0 <= confidence <= 1
        judgments = {}
        for output_name, capture_name in NOUL_FIELDS.items():
            answer = answers[capture_name]
            value = answer["noul"]
            assert answer["type"] == "noul"
            assert isinstance(value, (int, float)) and 0 <= value <= 1
            judgments[output_name] = value
        results.append({
            "id": record["id"],
            "category": category,
            "category_confidence": confidence,
            **judgments,
            "route": route(judgments),
        })

    with (ROOT / "experiment6-results.jsonl").open("x") as output:
        for result in results:
            output.write(json.dumps(result, separators=(",", ":")) + "\n")
    print(f"Wrote {len(results)} offline routes to experiment6-results.jsonl")


if __name__ == "__main__":
    main()
