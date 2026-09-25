# jev-lab

A small experiment with TypeSafe Jev as a cheap, bounded decision layer for technical records. It asks Jev to choose a record type and estimate four yes/no properties. It evaluates classification and decision behavior, not summarization.

The synthetic records resemble notes from the old Recall project: decisions, completed changes, debugging, and ambiguous fragments. This repo is independent of Recall and uses no Recall data or code.

## Experiments

Experiment 1 used the ten unchanged records in `records.jsonl`. Its captured responses are preserved in `experiment1-results.jsonl`; the CLI does not write to that file.

Experiment 2 uses `experiment2-records.jsonl`: the same ten records in the same order, followed by twenty harder contrasts. These include proposed versus completed work, ongoing versus fixed incidents, a decision reversal, a failed experiment, transient logs and status, consequential versus mundane observations, and records with different amounts of surrounding context. The added records are synthetic, so their wording and expected distinctions can be inspected directly.

Run from an interactive zsh shell, which loads `~/.config/openrouter/env` if it exists:

```sh
cd ~/labs/repos/jev-lab
cargo run
```

The Rust CLI runs Experiment 2: it makes one sequential OpenRouter Decisions API request per record, prints the selected category and Noul probabilities, and writes the complete API response (including Choice probabilities) plus latency to ignored `experiment2-results.jsonl`. It reports total input tokens, reported cost, and average request latency. A missing key stops before any request or result file is created. A failed request stops the run; results from earlier records remain in `experiment2-results.jsonl`.

Later, the same records and rubric may be used to compare Jev with a conventional LLM using structured output. This initial experiment does not include that comparison or confidence thresholds.
