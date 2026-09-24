# jev-lab

A small experiment with TypeSafe Jev as a cheap, bounded decision layer for technical records. It asks Jev to choose a record type and estimate four yes/no properties. It evaluates classification and decision behavior, not summarization.

The ten synthetic records resemble notes from the old Recall project: decisions, completed changes, debugging, and ambiguous fragments. That mix makes it possible to inspect where a fixed rubric works and where context or category boundaries cause uncertainty. This repo is independent of Recall and uses no Recall data or code.

Run from an interactive zsh shell, which loads `~/.config/openrouter/env` if it exists:

```sh
cd ~/labs/repos/jev-lab
cargo run
```

The Rust CLI makes one sequential OpenRouter Decisions API request per record, prints the selected category and Noul probabilities, and writes the complete API response (including Choice probabilities) plus latency to ignored `results.jsonl`. It reports total input tokens, reported cost, and average request latency. A missing key stops before any request or result file is created. A failed request stops the run; results from earlier records remain in `results.jsonl`.

Later, the same records and rubric may be used to compare Jev with a conventional LLM using structured output. This initial experiment does not include that comparison or confidence thresholds.
