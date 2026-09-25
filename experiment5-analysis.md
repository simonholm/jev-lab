# Experiment 5: real project-history records — interrupted

## Freeze and input

The baseline worktree was clean before Experiment 5, and `main` and the cached
`origin/main` both resolved to `72513eed39365b447e1b2e54c960b09a8d1abb47`.
Experiment 3's rubric and labels and Experiment 4's comparison procedure were
inspected. Neither previous experiment was run or changed.

`experiment5-build-dataset.py` selected 61 existing records from eight local
project repositories: 25 Git commit subjects and 36 verbatim file excerpts.
The source repositories were read only. `experiment5-records.jsonl` stores the
original text and audit provenance; the runners deserialize and send only each
record's `text`. The separate `experiment5-expected.jsonl` contains manually
assigned Experiment 3 labels and short rationales, including difficult cases.
No synthetic records or class-balancing rewrites were used. A scan of selected
texts found no credential-like values.

The labels and all 61 selected records were frozen before any Experiment 5 API
attempt. `experiment5-freeze.json` records the UTC freeze timestamp, model IDs,
baseline commit, and SHA-256 hashes of the dataset, labels, rubrics, and runners.
The frozen label hash is
`db5fbbe15143fc6f888e90537791c620d5093a0dd6dde7dff621e52116260813`;
the record hash is
`61f0b7c2453dac02eb08811f257e78a49d1c45b45fc9f65d1f647bcd438cdce7`.
The expected categories are 20 implementation, 13 observation, 11 discussion,
9 troubleshooting, and 8 decision. Expected yes counts are 8 explicit decisions,
25 completed changes, 41 history records, and 13 records missing required context.

The dedicated Jev and Gemini runners copy the Experiment 3 Decisions API rubric
and Experiment 4 JSON-schema procedure respectively. They preserve record order,
capture raw responses, and use new result files opened with `create_new`.
`cargo check --offline --bins` passed before any model call.

## Interrupted Jev run

The first and only Experiment 5 model attempt targeted `e5-01` with
`typesafe/jev-1.13`. The request failed at transport level after about 0.0014 s:
`error sending request for url (https://openrouter.ai/api/alpha/decisions)`.
There was no HTTP status, response body, token count, cost, or model answer.
The failure is preserved in `experiment5-jev-results.jsonl`; the command output
is in `experiment5-jev-run.log`. The interactive shell also reported denied
writes to its cache and completion dump, which may be related to the restricted
execution environment. The exact network cause was not established.

Per the predeclared failure rule, no failed record was rerun, no gaps were
filled, and Gemini was not called. There are zero completed records for either
model, so category, binary-judgment, operational, and synthetic-versus-real
comparisons cannot be reported from this attempt. The frozen labels remain
unchanged.
