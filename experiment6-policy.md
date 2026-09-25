# Experiment 6: frozen offline routing policy

For one already-captured Jev response, read the four Noul probabilities. Apply
these rules in order:

1. `KEEP` if retain-for-history is at least 0.8, missing-required-context is
   below 0.8, and either explicit-decision or completed-change is at least 0.8.
2. Otherwise, `DEEP_REVIEW` if retain-for-history, explicit-decision, or
   completed-change is at least 0.5.
3. Otherwise, `DROP`.

`experiment6-policy.py` is the executable form of these rules. The policy reads
no record text, provenance, human label, or model output beyond the permitted
bounded judgments. It does not use category or category confidence: Experiments
3 and 4 found mixed-event category boundaries, so category is not a reliable
hard routing gate. Experiment 4 also found many high missing-context scores on
self-contained records; context therefore blocks only automatic retention at a
strong 0.8 signal. The 0.5 level is the earlier descriptive yes/no reference
point, and 0.8 denotes a stronger signal for automatic retention. These values
were chosen before applying the policy to Experiment 5 Jev responses. They are
not calibrated probabilities or thresholds optimized on these 61 records.
