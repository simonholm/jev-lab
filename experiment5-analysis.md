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

The first Experiment 5 model attempt targeted `e5-01` with
`typesafe/jev-1.13`. The request failed at transport level after about 0.0014 s:
`error sending request for url (https://openrouter.ai/api/alpha/decisions)`.
There was no HTTP status, response body, token count, cost, or model answer.
The failure is preserved locally in the ignored
`experiment5-jev-attempt1-results.jsonl` (SHA-256
`20abcf16cd2f1362cc8ccefaf4c13138f2dd51daad07d4357b99e0f12fa9c942`);
the command output is in `experiment5-jev-run.log`. The interactive shell also
reported denied writes to its cache and completion dump. Later probing showed
that an in-sandbox request could not resolve `openrouter.ai`, while the same
endpoint returned an HTTP response outside the network sandbox. The restricted
network environment caused the transport failure; the cache warnings were
incidental.

Per the predeclared failure rule, no failed record was rerun and no gaps were
filled in attempt 1. Gemini was not called during that attempt.

## Second execution attempt

The frozen state was committed as `803ee3881a3ce33dc0d2348e52b624c8e7be72fe`
and pushed before another model request. The first raw capture was retained under
its attempt-specific filename. Attempt 2 ran outside the network sandbox, from
`e5-01`, with the unchanged runner, rubric, model, record order, and labels.

Jev completed all 61 records sequentially, with 61 distinct response IDs and no
HTTP or model errors. Its captured IDs and texts match the frozen input in order.
The runner reported 50,280 input tokens, $0.002111760 API cost, and 16.711 s
full-run wall time; the raw responses also report 8,327 output tokens. The
ignored Jev capture is `experiment5-jev-results.jsonl` (SHA-256
`449fc8796e5e1acfcb7f5b54b1a567b47b06ab99c3c9ce0575a58a3dd0b0ae73`).

Only after Jev completed did Gemini run, once, on the same ordered records. It
validated responses for `e5-01` through `e5-07`. The eighth HTTP response was
captured for `e5-08`, but its `finish_reason` was `error` and its answer ended in
the middle of a JSON number (`"explicit_decision": 0.`). The runner stopped on
the JSON parse error. There were seven valid Gemini answers, one invalid captured
answer, and no requests for `e5-09` through `e5-61`. The ignored partial capture
is `experiment5-gemini-results.jsonl` (SHA-256
`96fe191894dce750ca2f5a1f14654c22436da158919f8887f0ff1c80f4913ea6`).
No record was retried and the partial Gemini run was not resumed.

The frozen manifest hashes still match every listed file, including the 61
records and 61 human labels. Because Gemini did not complete, this is not a full
paired comparison; category, four-judgment, disagreement, and synthetic-versus-real
results are intentionally not reported from the partial run.

Offline `cargo check --bins` and `cargo test` pass, as does `git diff --check`.
`cargo fmt --check` reports formatting differences in the frozen Jev runner;
that runner was left untouched to preserve its manifest hash.
