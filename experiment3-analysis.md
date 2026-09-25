# Experiment 3: explicit rubric

## Frozen design (written before the Experiment 3 call)

Experiment 3 changes only the category and four Noul question wording in the Jev request; the CLI's output path changes to keep responses separate. It sends the same 30 records, in the same order, from `experiment2-records.jsonl`; the answer keys, model identifier, endpoint, sequential request flow, and raw response format are unchanged. The expected labels in `experiment3-expected.jsonl` are separate from the request state and are not read by the CLI. No labels are chosen from Experiment 3 answers.

Input SHA-256: `d3b298cb1b3eeb6145514bd4b77afe7d78575714fd04fd98baf2f77b47164600`. Experiment 1 capture SHA-256: `ce820759e6a07fbb13b04e0ffb98d98d36fe91953f4edaee0b18537522b58a39`. Experiment 2 capture SHA-256: `bda00160669372d779ec81f9bfa58f796176c67b6f1a2dfc8086cabe466c88c8`.

The baseline is the existing Experiment 2 capture from `typesafe/jev-1.13-20260917`: 30 responses, 15,935 input tokens, reported cost $0.000669270, and mean request latency 0.333 seconds. Its category choices matched the human primary-category reading on 28/30 records, with r16 (historical observation called implementation) and r28 (unapproved proposal called decision) as mismatches. r18 (raw path) and r21 (failed experiment with a revert) have debatable primary categories. On the prior human Noul labels, Experiment 2's expected-yes versus expected-no mean probabilities were: decision 0.917 vs 0.424, change 0.906 vs 0.205, history 0.731 vs 0.532, and context 0.763 vs 0.683. These are descriptive results from this synthetic set, not calibrated probabilities.

The Experiment 3 category labels retain the same human primary-category reading. The four yes/no label definitions are now:

Frozen expected-label SHA-256: `712ac22b0d526010d41a0dcdcf411c7a7e6ba2e0e5aea67c96d52eba020b12c3`. The file contains 30 IDs in input order: four expected explicit decisions, nine completed changes, 14 history records, and four records missing required context.

- `concrete_decision`: explicit decision, approval, rejection, or policy choice; an action alone is insufficient.
- `completed_change`: a stated completed or applied project change, including a project environment correction, a reverted boost, or an index repair; a decision or past-behavior description alone is insufficient.
- `project_history`: retain an explicit decision, completed project change, significant resolved problem, failed experiment that changed subsequent work, or significant project result. Exclude casual discussion, proposals, transient status, and routine output.
- `needs_context`: the record omits information required to identify its project event or result. More background being useful is insufficient.

Compared with the Experiment 2 human labels, `project_history` changes from yes to no for r05, r06, r08, r09, r13, r14, r28, and r30. These are unresolved discussion or proposals, a state with no identified change, or unresolved problems; the new retention rule excludes them. `needs_context` changes from yes to no for r07, r09, and r14: each identifies its change or problem despite omitted background. The explicit-decision and completed-change labels do not change. The category labels do not change.

Some boundaries remain judgment calls: r18 is labeled observation because it reports a path, though it has no meaningful project result; r21 is labeled troubleshooting because the failed boost was diagnosed and reverted; r25 needs context because the bare health-check line does not identify a project or service. These choices were made before seeing Experiment 3 answers. Compare both experiments against these same frozen labels when assessing wording effects; do not attribute any change caused only by label definitions to Jev.

## Captured results

One sequential run completed all 30 records. The ignored `experiment3-results.jsonl` contains each raw response, matched by ID and record text to the unchanged input. Its SHA-256 is `7b0bffc61a9a0c0bce4f54ef4c73d465ec46aa7845f40c418de8231fd65ef935`. The returned model was `typesafe/jev-1.13-20260917` for every record. Experiment 3 used 24,605 input tokens, reported $0.001033410 cost, and averaged 0.301 seconds per request. The longer rubric increased input tokens and reported cost by about 54% versus Experiment 2.

The table evaluates **both** captures against the same frozen Experiment 3 labels. A yes/no prediction is counted as yes at probability 0.5; this is a descriptive cutoff, not an optimized threshold. "Gap" is mean probability on expected-yes records minus mean probability on expected-no records.

| Question | Expected yes/no | E2 yes/no means; gap | E3 yes/no means; gap | E2 false yes/no | E3 false yes/no |
| --- | ---: | ---: | ---: | ---: | ---: |
| Explicit decision | 4/26 | 0.917 / 0.424; 0.494 | 0.975 / 0.115; 0.860 | 10 / 0 | 0 / 0 |
| Completed change | 9/21 | 0.906 / 0.205; 0.701 | 0.890 / 0.140; 0.750 | 3 / 0 | 2 / 0 |
| Retain for history | 14/16 | 0.759 / 0.608; 0.152 | 0.870 / 0.217; 0.652 | 14 / 1 | 2 / 0 |
| Missing required context | 4/26 | 0.693 / 0.703; -0.011 | 0.825 / 0.616; 0.209 | 24 / 1 | 20 / 0 |

Category matches remained 28/30 on the same human labels. Experiment 2 missed r16 (implementation instead of observation, confidence 0.22) and r28 (decision instead of discussion, 0.81). Experiment 3 corrected both: r16 became observation at 0.41 and r28 discussion at 0.93. It instead labeled r15 implementation rather than troubleshooting (0.62) and r21 observation rather than troubleshooting (0.45). Both new mismatches mix a fix or revert with the problem or result that prompted it, so their single primary label remains debatable. The other 26 category choices were unchanged.

The explicit-decision question shows the clearest wording effect. For example, r02 fell from 0.87 to 0.09, r12 from 0.93 to 0.12, r15 from 0.95 to 0.07, and r27 from 0.94 to 0.07; all are completed actions without an explicit decision. The four explicit decisions scored 0.97–0.98 in Experiment 3. The completed-change question also improved, but still marked the historical behavior r16 at 0.51 and the decision-only r20 at 0.71; r11, another decision without implementation, fell from 0.67 to 0.32.

History retention improved on routine or inconsequential records: r04 fell from 0.69 to 0.09, r05 from 0.69 to 0.14, and r22 from 0.68 to 0.09. The remaining false yes records are unresolved investigations r09 (0.56) and r14 (0.54), which the frozen retention rule excludes because neither states a resolution. The clearer context question helped r25 (bare health-check log) rise from 0.28 to 0.73, but it still scores self-contained r04 at 0.76 and r24 at 0.87. Twenty of 26 expected-no records remain above 0.5. This is the weakest rubric even after clarification.

On this fixed synthetic dataset, the large decision and history improvements support ambiguous wording as a major cause of their Experiment 2 weakness. They do not show that Jev alone was the cause. The category result does not improve in count, and the persistent context and completed-change errors leave model behavior, overlapping definitions, and human-label judgment entangled. This was one run per rubric, with longer Experiment 3 questions and no repeatability estimate for that rubric; the numbers describe these captures rather than general performance or calibration.
