# Experiment 4: Jev versus one general-purpose LLM

## Frozen comparison

This compares the existing Experiment 3 Jev capture with one new, sequential 30-record run of `google/gemini-2.5-flash-lite` through OpenRouter chat completions. No Jev request was repeated. Both sides use the same record order and texts from `experiment2-records.jsonl`, the same category definitions and four question wordings from Experiment 3, and the same human labels in `experiment3-expected.jsonl`. The labels were never included in model requests. The general model returned only a fixed JSON object with the category, category confidence, and four probabilities; there was no explanation request.

The input SHA-256 is `d3b298cb1b3eeb6145514bd4b77afe7d78575714fd04fd98baf2f77b47164600`; the frozen labels SHA-256 is `712ac22b0d526010d41a0dcdcf411c7a7e6ba2e0e5aea67c96d52eba020b12c3`. The untouched Experiment 3 Jev capture SHA-256 is `7b0bffc61a9a0c0bce4f54ef4c73d465ec46aa7845f40c418de8231fd65ef935`. The ignored Experiment 4 raw capture SHA-256 is `0633e90e8055a0f049c8b732282b7b64c6e2030b30953342738c72e5262cc18c`. All four files have 30 records; each captured ID and text matches the input at the same position. Experiment 4 contains 30 successful responses from the one run, with unique response IDs and the selected model in each response.

OpenRouter advertised `google/gemini-2.5-flash-lite` at **$0.10 per million input tokens and $0.40 per million output tokens** when selected on 2026-09-25. It is a mainstream, inexpensive general-purpose Gemini model, and OpenRouter lists JSON-schema structured output support for it. The runner uses `/api/v1/chat/completions` with `response_format: json_schema`, `strict: true`, and `provider.require_parameters: true`. These advertised rates explain the choice; the operational comparison below uses the API's reported costs. Sources: [model and pricing](https://openrouter.ai/google/gemini-2.5-flash-lite), [structured-output requirements](https://openrouter.ai/docs/guides/features/structured-outputs), [chat completion endpoint](https://openrouter.ai/docs/quickstart).

## Category

Both models match **28/30** expected primary categories. They miss exactly the same records: r15 is expected `troubleshooting` but both say `implementation` (Jev confidence 0.62; Gemini 0.90); r21 is expected `troubleshooting` but both say `observation` (Jev 0.45; Gemini 0.90). The expected primary category is debatable for these mixed repair/result records. The two models agree on all 30 category choices: 28 jointly correct, two jointly wrong, and no category case where one alone is correct. Both call r16 `observation` and r28 `discussion`, correcting the earlier Experiment 2 category failures without changing the frozen Experiment 3 labels.

## Four bounded judgments

The counts use the frozen expected yes/no labels. Means are probabilities on expected-yes and expected-no records; gap is yes mean minus no mean. Pairwise separation is the number of expected-yes/expected-no pairs where the yes probability is **strictly greater** than the no probability, divided by all such pairs. Ties do not count as wins. False yes/no use 0.5 only as a descriptive reference point; no threshold was tuned.

| Judgment | Expected yes/no | Jev yes/no means; gap | Gemini yes/no means; gap | Jev pairwise | Gemini pairwise | Jev false yes/no | Gemini false yes/no |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Explicit decision | 4/26 | 0.975 / 0.115; 0.860 | 1.000 / 0.004; 0.996 | 104/104 | 104/104 | 0 / 0 | 0 / 0 |
| Completed change | 9/21 | 0.890 / 0.140; 0.750 | 0.800 / 0.000; 0.800 | 189/189 | 168/189 (21 ties) | 2 / 0 | 0 / 2 |
| Retain for history | 14/16 | 0.870 / 0.217; 0.652 | 0.914 / 0.244; 0.671 | 224/224 | 212/224 (8 ties) | 2 / 0 | 4 / 0 |
| Missing required context | 4/26 | 0.825 / 0.616; 0.209 | 0.850 / 0.169; 0.681 | 92/104 (1 tie) | 104/104 | 20 / 0 | 1 / 0 |

At 0.5, Jev's completed-change false yes records are r16 (0.51, historical behavior) and r20 (0.71, decision without application). Gemini avoids both, but misses completed changes in r21 (0.0, reverted boost) and r29 (0.2, index repair). Both give explicit decisions to the four labeled decisions and reject the earlier action-only failures r02, r12, r15, and r27. Both correctly identify the absence of an approved decision in r28; Jev gives 0.29 and Gemini 0.0.

For history, both retain unresolved investigations r09 and r14 against the frozen label; Gemini also retains discussion r05 at exactly 0.5 and unresolved compatibility observation r30 at 0.7. Both retain r16's significant historical result and r21's failed experiment. For missing context, both identify r08, r18, r23, and r25. Jev still gives at least 0.5 to 20 self-contained records; Gemini does so only for routine r17, at exactly 0.5. The difficult self-contained r04 and r24 are 0.76/0.87 from Jev versus 0.3/0.2 from Gemini. The bare health log r25 is 0.73 versus 1.0. These are useful operational scores but are **not calibrated probabilities**; a general LLM's self-reported numbers need not share the probabilistic semantics of Jev's Noul outputs.

At the record level, the category choices are identical, so the meaningful one-sided cases are binary judgments. Jev is correct and Gemini wrong on completed-change r21 and r29, and on Gemini's extra history false yes records r05 and r30. Gemini is correct and Jev wrong on completed-change r16 and r20 and on 19 of Jev's 20 context false yes records (all except r17). They agree and are wrong on category r15/r21 and history r09/r14; they agree and are correct on explicit-decision labels throughout, category r16/r28, and the four positive missing-context labels. The r15 category disagreement with the human label does not imply either model missed the explicit completed change in that record.

## Operational measurements

| Measurement | Existing Jev Experiment 3 | Gemini Experiment 4 |
| --- | ---: | ---: |
| Input tokens reported | 24,605 | 13,115 |
| Output tokens reported | 4,114 | 2,224 |
| Total API-reported cost | $0.001033410 | $0.002201100 |
| API-reported cost per record | $0.000034447 | $0.000073370 |
| Sum of captured request latencies | 9.037 s | 12.517 s to HTTP headers |
| Average captured request latency | 0.301 s | 0.417 s to HTTP headers |
| Full run wall time | not recorded in Experiment 3 | 17.872 s (0.596 s per record) |

The Gemini timer stopped when response headers arrived; its JSON body parsing occurred after that timestamp. Its full wall time includes response bodies, parsing, file writes, and console output. Jev's captured latency includes response JSON parsing; its full wall time was not recorded. Therefore the recorded latency figures are **not identically measured**, and no exact full-run speed ratio is justified. The requests were sequential, but summing Jev request latencies is not a measured full-run wall time. Tokenizers and API accounting also differ, so raw token counts are not an apples-to-apples efficiency measure. The actual reported total cost of this Gemini run is about 2.13 times Jev's, despite fewer reported tokens.

## Interpretation and limits

On classification, Jev and Gemini make the same 30 choices, including two mixed-event disagreements with the human primary labels. For explicit decisions, both separate the frozen labels perfectly here. On completed changes and history, Jev gives stronger strict pairwise ordering but has some false yes at 0.5; Gemini has sharper negative scores but misses two completed repairs and retains two additional nonhistory records. For missing context, Gemini separates the four positives from all negatives while Jev has a broad high-score tendency on self-contained records. The probabilities remain operational ranking and cutoff signals, not evidence of calibration.

Jev is a useful specialized bounded-decision primitive here because it returns the category and four bounded answers directly, with lower reported cost and short captured request times. The conventional LLM is also a viable structured-judgment implementation and handles missing-context boundaries much better in this capture. The Gemini path requires a longer rubric prompt, JSON schema, parsing, and range checks; Jev requires its Decisions API question structure and answer parsing. Both fit in a small Rust client. The differences may arise from model behavior, from how the same rubric is encoded as Jev Choice/Noul questions versus a single system prompt and JSON schema, or from both; this experiment cannot isolate those causes.

The 30 records are synthetic and small, one run per model/rubric was captured, the labels have some subjective primary-category boundaries, and neither model's scores were tested for repeatability or calibration. This is exploratory evidence about these specific artifacts, not a benchmark or an overall winner. A sensible next experiment would use a new, independently labeled set of real project records under the same frozen rubric and one predeclared run per model; it is not part of Experiment 4.
