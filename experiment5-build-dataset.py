"""Extract the preselected real records and frozen human labels for Experiment 5.

Run once before either model. Source repositories are read only. The selection
and labels below are part of the experiment design, not model input.
"""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOS = Path.home() / "labs/repos"

# repo, commit-prefix or file path, line range, category, decision, change,
# history, missing context, rationale. C = commit subject; F = file lines.
SPECS = [
    ("C", "recall", "53e1894", "implementation", 0, 1, 1, 0, "The subject records a retrieval feature being added."),
    ("C", "recall", "266e1dd", "troubleshooting", 0, 1, 1, 0, "A named broad temporal retrieval fault was fixed; repair is the main event."),
    ("C", "recall", "81c96f4", "implementation", 0, 1, 1, 0, "The default model was switched; no explicit choice rationale is stated."),
    ("C", "recall", "9e8af14", "implementation", 0, 1, 1, 0, "Claude Code session ingestion was added."),
    ("C", "recall", "559385a", "implementation", 0, 1, 1, 0, "An answer-framing change was made; the title is terse but identifies it."),
    ("C", "recall", "85d5c52", "troubleshooting", 0, 1, 1, 0, "A specific latest-state evidence fault was fixed."),
    ("C", "disk-agent", "898f9e0", "implementation", 0, 1, 1, 0, "Snapshot timestamps were added."),
    ("C", "disk-agent", "e2447fd", "implementation", 0, 1, 1, 0, "Retained-version detection was added."),
    ("C", "disk-agent", "925bc11", "troubleshooting", 0, 1, 1, 0, "The title records repair of hidden unclassified growth."),
    ("C", "disk-agent", "1523243", "implementation", 0, 1, 1, 0, "A significant Rust migration was completed."),
    ("C", "disk-agent", "3ff4849", "implementation", 0, 1, 1, 0, "Warning presentation was changed; significance is debatable but this is a durable UX change."),
    ("C", "disk-agent", "52a7c18", "implementation", 0, 1, 1, 0, "The investigate command was refactored into a live diagnostic."),
    ("C", "disk-maint", "5a9a121", "implementation", 0, 1, 1, 0, "Empty local targets were hidden in output."),
    ("C", "disk-maint", "eac1dd5", "implementation", 0, 1, 1, 0, "Empty scan sections were hidden; small but durable behavior."),
    ("C", "disk-maint", "5db0b53", "implementation", 0, 1, 1, 0, "A target cleanup workflow was completed."),
    ("C", "job-ad", "647a07c", "troubleshooting", 0, 1, 1, 0, "Pagination and end-date defects were repaired."),
    ("C", "job-ad", "22d3c65", "implementation", 0, 1, 1, 0, "Filtered job-ad ranges were added."),
    ("C", "job-ad", "0d5d576", "implementation", 0, 1, 1, 0, "An initial fetcher was added."),
    ("C", "reel2text", "aa1a9e5", "observation", 0, 0, 1, 0, "The documented ASR limitation is the substantive result; a documentation commit could also be called implementation."),
    ("C", "reel2text", "ce80d24", "implementation", 0, 1, 1, 0, "An enhanced audio-processing variant was added."),
    ("C", "reel2ocr", "1ee7561", "troubleshooting", 0, 1, 1, 0, "Real-device deduplication and portability defects were repaired."),
    ("C", "reel2ocr", "afc7721", "implementation", 0, 1, 0, 0, "Temporary debug artifacts were removed; routine cleanup is not a concise history event."),
    ("C", "reel2ocr", "14f51ea", "implementation", 0, 1, 1, 0, "The Android wrapper was extended to search two directories."),
    ("C", "codex-session-tools", "7382836", "implementation", 0, 1, 1, 0, "Evidence and presentation were separated; title does not explicitly say a policy choice was made."),
    ("C", "codex-session-tools", "7e11f70", "implementation", 0, 1, 0, 0, "A routine initial scaffold was created; retention boundary is debatable."),

    ("F", "reel2text", "NOTE.md:5-8", "observation", 0, 0, 1, 0, "A significant mixed success and empty-transcript result is reported; no fix is claimed."),
    ("F", "reel2text", "NOTE.md:12-16", "troubleshooting", 0, 0, 1, 0, "The audio cause and Whisper symptom are diagnosed, but not resolved."),
    ("F", "reel2text", "NOTE.md:20-20", "observation", 0, 0, 0, 1, "'File detection: works' lacks the project event or result being checked."),
    ("F", "reel2text", "NOTE.md:21-21", "observation", 0, 0, 0, 1, "A bare component check does not identify the investigation."),
    ("F", "reel2text", "NOTE.md:22-22", "observation", 0, 0, 0, 1, "The checked invocation is named, but the relevant problem/result is absent."),
    ("F", "reel2text", "NOTE.md:23-23", "observation", 0, 0, 0, 1, "A bare verification line omits which repository and drift concern."),
    ("F", "reel2text", "NOTE.md:27-28", "observation", 0, 0, 1, 0, "The input-audio limitation is intelligible and significant."),
    ("F", "reel2text", "NOTE.md:32-33", "decision", 1, 0, 1, 0, "The script intentionally avoids preprocessing; this is an explicit design choice alongside a measurement."),
    ("F", "reel2ocr", "STATUS.md:5-8", "decision", 1, 0, 1, 0, "The primary development and synchronization workflow is stated as policy; no new change is asserted."),
    ("F", "reel2ocr", "STATUS.md:14-19", "observation", 0, 0, 0, 1, "The list of implemented components lacks its heading/project and does not by itself state when any change was carried out."),
    ("F", "reel2ocr", "STATUS.md:23-26", "observation", 0, 0, 1, 0, "Specific OCR limitations are stated without a repair."),
    ("F", "reel2ocr", "STATUS.md:30-31", "discussion", 0, 0, 0, 0, "A future validation and conditional tuning task, not an applied change."),
    ("F", "reel2ocr", "STATUS.md:35-38", "decision", 1, 0, 1, 0, "Deletion is explicitly deferred with a reason; the excerpt is mixed with future conditions."),
    ("F", "reel2ocr", "ARCHITECTURE.md:59-63", "troubleshooting", 0, 0, 1, 0, "A failed rewrite and abandonment affecting subsequent work are documented; category mixes diagnosis and decision."),
    ("F", "recall", "docs/design/retrieval-planner.md:5-8", "observation", 0, 0, 1, 0, "Current lexical retrieval behavior is documented as the motivating problem."),
    ("F", "recall", "docs/design/retrieval-planner.md:20-30", "troubleshooting", 0, 0, 1, 0, "Natural time questions are shown to fail and the mechanism is explained; no repair is claimed."),
    ("F", "recall", "docs/design/retrieval-planner.md:38-45", "observation", 0, 0, 1, 1, "The measured zero matches are significant, but the excerpt starts mid-investigation and omits the query."),
    ("F", "recall", "docs/design/retrieval-planner.md:47-55", "troubleshooting", 0, 0, 1, 0, "Mandatory lexical terms are identified as the failure mechanism."),
    ("F", "recall", "docs/design/retrieval-planner.md:75-83", "discussion", 0, 0, 0, 0, "A proposed ask-only planner and constraints are stated, without approval or implementation."),
    ("F", "recall", "docs/design/retrieval-planner.md:106-112", "discussion", 0, 0, 0, 0, "A planner architecture is proposed; 'should' does not assert completion."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:5-12", "discussion", 0, 0, 0, 0, "Benchmark scope is proposed; the normative wording could be read as policy but the section does not say it was approved."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:25-28", "discussion", 0, 0, 0, 0, "The text proposes durable fixtures and contrasts manual smoke checks."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:32-34", "discussion", 0, 0, 0, 1, "A rationale for JSON is supplied, but the excerpt omits what 'case' is or whether JSON was adopted."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:70-71", "discussion", 0, 0, 0, 1, "An implementation recommendation refers to an unexplained 'first implementation'."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:75-83", "discussion", 0, 0, 0, 0, "A future runner behavior is specified but not reported as built."),
    ("F", "recall", "docs/design/retrieval-evaluation.md:98-99", "discussion", 0, 0, 0, 1, "Top-k pass criteria are given without naming the benchmark or what is ranked."),
    ("F", "codex-session-tools", "PROJECT_NOTES.md:7-10", "decision", 1, 0, 1, 0, "Explicit working rules choose source of truth, evidence before code, and disposable indexes."),
    ("F", "codex-session-tools", "PROJECT_NOTES.md:23-25", "discussion", 0, 0, 0, 1, "Planned improvements are listed without their project or current implementation context."),
    ("F", "codex-session-tools", "PROJECT_NOTES.md:27-29", "observation", 0, 0, 0, 1, "An inventory under 'Implemented' reports capabilities but omits the project; it does not date a change."),
    ("F", "codex-session-tools", "PROJECT_LOG.md:5-5", "observation", 0, 0, 0, 1, "A dated inspection mentions 'recent real session JSONL files' but not a substantive result."),
    ("F", "codex-session-tools", "PROJECT_LOG.md:7-7", "implementation", 0, 1, 1, 0, "A dated log says session-browser commands were added."),
    ("F", "ideas", "development-memory.md:34-34", "decision", 1, 0, 1, 0, "The principle explicitly directs structured extraction before AI interpretation."),
    ("F", "ideas", "development-memory.md:40-40", "decision", 1, 0, 1, 0, "Rust is explicitly named as the preferred implementation language."),
    ("F", "ideas", "development-memory.md:44-44", "decision", 1, 0, 1, 0, "Local-first operation is explicitly chosen as the default."),
    ("F", "ideas", "development-memory.md:46-46", "decision", 1, 0, 1, 0, "An explicit policy against premature platform definition is stated."),
    ("F", "ideas", "development-memory.md:75-75", "discussion", 0, 0, 0, 1, "'These components' has no referent in the isolated excerpt; future possibilities are not an adopted roadmap."),
]


def main():
    records = []
    labels = []
    for index, (kind, repo, source, category, decision, change, history, context, rationale) in enumerate(SPECS, 1):
        repo_path = REPOS / repo
        if kind == "C":
            full_sha = subprocess.check_output(["git", "-C", str(repo_path), "rev-parse", source], text=True).strip()
            text = subprocess.check_output(["git", "-C", str(repo_path), "show", "-s", "--format=%s", full_sha], text=True).rstrip("\n")
            provenance = {"repository": repo, "source_type": "git_commit_subject", "commit": full_sha}
        else:
            path, span = source.rsplit(":", 1)
            start, end = map(int, span.split("-"))
            all_lines = (repo_path / path).read_text().splitlines(keepends=True)
            text = "".join(all_lines[start - 1:end]).rstrip("\n")
            provenance = {"repository": repo, "source_type": "file_lines", "path": path, "line_start": start, "line_end": end, "source_sha256": hashlib.sha256((repo_path / path).read_bytes()).hexdigest()}
        record_id = f"e5-{index:02d}"
        records.append({"id": record_id, "text": text, "provenance": provenance})
        labels.append({"id": record_id, "category": category, "concrete_decision": bool(decision), "completed_change": bool(change), "project_history": bool(history), "needs_context": bool(context), "rationale": rationale})
    assert len(records) == len(labels) == 61
    for filename, rows in [("experiment5-records.jsonl", records), ("experiment5-expected.jsonl", labels)]:
        with (ROOT / filename).open("x") as output:
            for row in rows:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
    for filename in ("experiment5-records.jsonl", "experiment5-expected.jsonl"):
        print(filename, hashlib.sha256((ROOT / filename).read_bytes()).hexdigest())
    print("frozen_utc", datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main()
