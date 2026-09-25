# Experiment 6: offline routing of real project records

## Question and freeze

Can the already-captured Jev judgments support a simple deterministic
`KEEP` / `DEEP_REVIEW` / `DROP` layer for a Recall-like project history? This is
the final experiment in the Jev investigation. It made zero API requests and
did not rerun or change Experiment 5.

The baseline working tree was clean; `HEAD`, local `main`, and cached
`origin/main` all resolved to `5f1783b2fcaca80a5bb0faff1fa84c2566547db1`.
Experiment 5 supplied 61 genuine records, 61 frozen human labels, and 61
successful Jev answers in the same order, with distinct response IDs and no
errors. Every Experiment 5 manifest hash matched. The Jev raw capture SHA-256
was `449fc8796e5e1acfcb7f5b54b1a567b47b06ab99c3c9ce0575a58a3dd0b0ae73`.

Human routing labels in `experiment6-expected.jsonl` were assigned from record
text, provenance, and the existing Experiment 5 human labels, without inspecting
per-record Jev probabilities. Each has a rationale. The only routing policy is
in `experiment6-policy.md` and `experiment6-policy.py`. Both artifacts existed
before calculating routes. `experiment6-freeze.json` records their hashes and
the UTC freeze time, `2026-09-25T06:59:17.731274+00:00`. Its SHA-256 values are:

| Frozen artifact | SHA-256 |
| --- | --- |
| Human routing labels | `a2152090aa5e0ef65bf277efafa2e0ea828a03f94fcf56f9859aa42d8468d46f` |
| Executable policy | `84a61c1108f5305a32cd8f1ec3128f54462a549a483c6ffbb971f21c4837f32c` |
| Policy explanation | `83b27545da1efe489d4ce620d3612a1c2e55302b331ae0565b4420cc1641b1d1` |

Blinding was not absolute across the conversation: the earlier Experiment 5 run
displayed some per-record probabilities. Those scores were not consulted while
assigning Experiment 6 labels or defining the policy. The capture was first
inspected systematically after the label and policy freeze.

The offline runner checked these hashes before reading the 61 Jev responses.
It passed only the four bounded probabilities to the policy, then stored each
ID, Jev category and confidence, four probabilities, and route in
`experiment6-results.jsonl` (SHA-256
`7e9f1681b21add621c4ba384db7ea7d90ca25cf15e9b1dcf95b6df7d95520cc2`).
Human expected routes were not policy inputs. No thresholds, labels, or rules
were changed after evaluation.

## Results

Exact matches: **17/61 (27.9%)**.

| Route | Human | Jev policy |
| --- | ---: | ---: |
| KEEP | 34 | 1 |
| DEEP_REVIEW | 11 | 38 |
| DROP | 16 | 22 |

| Human \\ predicted | KEEP | DEEP_REVIEW | DROP |
| --- | ---: | ---: | ---: |
| KEEP | 1 | 24 | 9 |
| DEEP_REVIEW | 0 | 7 | 4 |
| DROP | 0 | 7 | 9 |

### Potentially destructive false drops

These 13 records would disappear before a more capable model could inspect
them. The history probability is shown because all 13 fell below the policy's
0.5 review threshold; their decision and change probabilities also fell below
0.5. The original text and rationale remain in the frozen artifacts.

| Record | Human route | Historically useful content | Jev history probability |
| --- | --- | --- | ---: |
| `e5-06` | KEEP | Latest-state evidence defect fixed | 0.34 |
| `e5-08` | KEEP | Retained application version detection added | 0.31 |
| `e5-14` | DEEP_REVIEW | Empty scan sections hidden; significance uncertain | 0.43 |
| `e5-18` | KEEP | Initial JobTech job-ad fetcher added | 0.25 |
| `e5-23` | KEEP | Android wrapper searches Movies and DCIM | 0.28 |
| `e5-24` | KEEP | Evidence separated from presentation | 0.28 |
| `e5-26` | DEEP_REVIEW | Mixed audio pipeline success and empty transcript result | 0.49 |
| `e5-32` | KEEP | Screen-recording audio is unsuitable for ASR | 0.22 |
| `e5-40` | DEEP_REVIEW | Current lexical retrieval behavior motivates later work | 0.34 |
| `e5-41` | KEEP | Natural time queries fail under lexical retrieval | 0.47 |
| `e5-42` | DEEP_REVIEW | Zero matches measured, but query context is incomplete | 0.14 |
| `e5-57` | KEEP | Structured data before AI is an explicit architecture principle | 0.42 |
| `e5-60` | KEEP | Avoiding premature platform definition is explicit policy | 0.49 |

### Other routing errors

- **Unnecessary downstream work:** Seven human `DROP` records went to
  `DEEP_REVIEW`: `e5-35`, `e5-37`, `e5-47`, `e5-48`, `e5-49`, `e5-51`, `e5-53`.
  They are incomplete inventory, future task, or unadopted proposal fragments.
- **Unnecessary retention:** No human `DROP` record went to `KEEP`.
- **Over-review:** 24 human `KEEP` records went to `DEEP_REVIEW`: `e5-01`,
  `e5-02`, `e5-03`, `e5-04`, `e5-05`, `e5-07`, `e5-09`, `e5-10`, `e5-12`,
  `e5-15`, `e5-16`, `e5-17`, `e5-19`, `e5-20`, `e5-21`, `e5-27`, `e5-33`,
  `e5-34`, `e5-38`, `e5-39`, `e5-43`, `e5-52`, `e5-58`, `e5-59`. These preserve
  information but consume downstream work.
- No human `DEEP_REVIEW` record went directly to `KEEP`.

## Architectural conclusion

This one predeclared policy is **not a useful autonomous routing layer** for
these 61 records. It drops 13/45 human `KEEP` or `DEEP_REVIEW` records, including
clear completed changes, diagnosed failures, and explicit principles. It sends
38/61 records to deeper review while automatically retaining only one. Of the
22 records it drops, 13 were potentially useful under the frozen human routes.
The main failure is upstream signal: several genuine changes and results have
Jev history probabilities below 0.5, so a simple history cutoff loses them.
Making the cutoff more permissive after seeing these outcomes would invalidate
this one-policy test.

These are judgments on one small, deliberately varied set with subjective
history boundaries. They do not show that every deterministic policy would fail.
They do show that this bounded-output policy cannot be trusted to discard real
project records without human or general-model review. Experimentation stops
here; no Experiment 7 is proposed.

The frozen Experiment 5 Jev runner has known `cargo fmt --check` differences.
It was left unchanged to preserve its hash.
