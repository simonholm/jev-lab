# jev-lab

An exploratory Rust evaluation of TypeSafe Jev as a bounded decision layer for
classifying and routing project-history records. The motivating question was
whether inexpensive, constrained judgments could simplify filtering in a
Recall-like history reconstruction pipeline.

## Conclusion

Jev produced useful bounded judgments on several narrowly defined tasks, and
precise rubric wording materially changed the results. Repeatability was not
established: each controlled condition has one captured run. On the synthetic
comparison, Gemini 2.5 Flash Lite produced broadly comparable structured
judgments, with different strengths and weaknesses. Jev then processed all 61
frozen real project records in Experiment 5.

The final routing policy matched **17/61 (27.9%)** human routes and made **13
potentially destructive false drops**: nine human `KEEP` and four human
`DEEP_REVIEW` records went to `DROP`. This experiment does not support using the
tested Jev plus deterministic-policy design as an automatic discard layer for
project-history reconstruction. Bounded judgments may still be useful as
metadata or decision support. These findings concern the captured runs and this
one policy, not Jev's general accuracy or suitability.

## Architecture tested

```text
real project record
        ↓
Jev bounded judgments
        ↓
ordinary deterministic policy
        ↓
KEEP / DEEP_REVIEW / DROP
```

Experiment 6 asked whether useful individual judgments compose into a safe
routing policy. Jev supplied a category, category confidence, and four bounded
judgments; the final route came from ordinary code, not model-generated history.

## Experiments

1. **Experiment 1:** Minimal feasibility test on ten synthetic technical records.
2. **Experiment 2:** Twenty harder synthetic records were added; ambiguous
   decision and history boundaries became apparent.
3. **Experiment 3:** The same 30 records were evaluated with a tighter, frozen
   rubric. Explicit-decision and history judgments improved substantially at
   the descriptive 0.5 cutoff; missing-context judgments remained weak.
4. **Experiment 4:** Controlled structured-output comparison with
   `google/gemini-2.5-flash-lite`. Jev and Gemini made identical category
   choices, matching the frozen primary labels on **28/30** records. Their four
   bounded judgments had different strengths and weaknesses.
5. **Experiment 5:** Sixty-one genuine records from eight pre-existing project
   repositories were human-labeled before inference. Jev completed **61/61**.
   Gemini produced seven valid answers, then stopped at `e5-08` with truncated
   JSON. No complete real-record model comparison was claimed.
6. **Experiment 6:** One frozen deterministic policy routed the existing 61 Jev
   answers entirely offline, with **zero model calls**. It matched **17/61**
   human routes and made **13 potentially destructive false drops**.

## Important findings

- Rubric precision mattered substantially, especially for explicit decisions
  and history retention. Narrow judgments worked better than vague contextual
  ones in the synthetic records.
- Category confidence did not guarantee correctness, especially on mixed events.
- Synthetic judgment performance did not imply successful routing of real
  records. Individual bounded judgments did not automatically compose into a
  reliable discard policy.
- A general-purpose model using structured output implemented a similar
  decision-layer pattern in the limited Experiment 4 comparison.
- API and harness reliability affected execution: Experiment 5 first hit a DNS
  restriction in its network sandbox; Gemini later returned truncated JSON.

## Methodology

Rust runners called OpenRouter with `typesafe/jev-1.13` and, for the controlled
comparison, `google/gemini-2.5-flash-lite`. Experiment 5 used genuine
pre-existing project records. Human labels were frozen before model execution
where required. Experiment 6 used a small Python policy and runner over the
existing Jev capture, with labels and policy frozen before evaluation. Its
thresholds were not optimized after seeing results. Raw API captures are kept
separate and ignored under the repository convention; the initial Experiment 1
capture remains a tracked baseline.

## Repository layout

- [`experiment3-analysis.md`](experiment3-analysis.md),
  [`experiment4-analysis.md`](experiment4-analysis.md),
  [`experiment5-analysis.md`](experiment5-analysis.md), and
  [`experiment6-analysis.md`](experiment6-analysis.md) give the detailed methods,
  measurements, and limits. Experiments 1 and 2 are described in the Experiment
  3 analysis.
- `experiment2-records.jsonl` and `experiment5-records.jsonl` are the synthetic
  and real-record inputs. `experiment3-expected.jsonl` and
  `experiment5-expected.jsonl` contain frozen human judgment labels.
- `experiment5-freeze.json` and `experiment6-freeze.json` record input and
  artifact hashes. `experiment6-expected.jsonl` holds human routes;
  `experiment6-policy.md` and `experiment6-policy.py` define the sole routing
  policy; `experiment6-results.jsonl` holds the offline routes.

## Limitations

These are small exploratory datasets, not a benchmark. Experiments 1–4 used
synthetic records; Experiment 5 had only 61 real records. Some mixed records
have subjective human labels. There was one captured run per controlled
condition, no repeatability estimate, and no probability calibration. Gemini's
Experiment 5 run was incomplete. Experiment 6 evaluated one predeclared policy,
not every possible policy. The results establish no general Jev-versus-Gemini
superiority.

## Status

The investigation is complete after Experiment 6. No Experiment 7 is planned.
