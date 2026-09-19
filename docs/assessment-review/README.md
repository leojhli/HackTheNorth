# Assessment-quality evidence

This directory records actual local inference on a fixed set of 20 synthetic explanations across five new code changes. The expected labels were written before the first run by the coding assistant. They are not independent human judgments.

## What the files mean

- `baseline.json`: the initial run. 16/20 outcomes matched expected labels, with zero false passes, two complete answers not passed and three operational failures. Counts overlap: one complete answer suffered an operational failure.
- `ordering-trial.json`: an unsuccessful intermediate change. Moving quotation extraction before the decision exposed that the model could omit the optional quotation field. The server correctly rejected unsupported passes. This trial is retained, not hidden.
- `required-quotes-trial.json`: evidence extraction made mandatory. It removed one unfair rejection, but malformed follow-ups still caused failures. Inspect the report for exact counts and latency.
- `synthetic-malformed-response.json`: a diagnostic generated only from the synthetic demo. It shows `decision: follow_up` combined with `next_question: null`. The public validator refused that contradictory response.
- `results.json`: latest run, saved incrementally; wait for its `summary` before treating it as complete. Includes expected labels, actual outcomes, feedback, errors and latency. A model or validation error is not counted as a correct follow-up.
- `HUMAN_REVIEW.md`: the latest human-review worksheet, with blank reviewer decisions. Earlier worksheets/results are archived on reruns.

The final response contract requires quotation evidence, asks for it before the decision, and requires a string for the follow-up field on the model wire. An empty string is normalized to null for a passing public result. A follow-up with no question remains invalid; the server never upgrades failures to passes.

## How to interpret the measurements

This set became a calibration set once it informed prompt/schema changes. Do not call later agreement a held-out accuracy score. False passes are measured at the accepted application outcome; a model attempting an invalid pass is separately visible as an operational failure. Twenty cases cannot establish general reliability or prompt-injection resistance.

The initial nullish-coalescing case exposed unfair feedback: the learner explicitly mentions missing type/range validation, but the model says that explanation is absent. This is an agent-identified quality issue to examine during human review. A server can validate structure and quotations, but cannot prove that every semantic judgment is correct.

Latency includes each evaluation request and validation, not the whole user journey. Cold loading and sustained GPU use affect results. Earlier runs reached more than 30 seconds per evaluation on this machine, so an isolated fast demo must not be presented as a sustained p95 guarantee. The PRD's ten-second latency target is unmet unless representative measurements establish otherwise.

The separate `../demo-rehearsal-result.json` uses model-generated questions and real API persistence/gating. It complements this fixed-question evaluation set. Neither file marks the required 20-answer human review or a real person's VS Code rehearsal complete.

## Question-generation defect found in the demo

The demo API flow completed, but its generated rubric incorrectly says `new Set(tags)` does not preserve tag order. JavaScript Set iteration preserves insertion order; spreading it preserves the first occurrence order. The complete learner answer correctly states that and was accepted. The vague-answer feedback also credits a mechanism the learner did not explain. These are semantic defects, not a clean assessment-quality pass. Fixed-question results do not cover question/rubric generation. Retain the raw evidence; question-generation review and new held-out cases are required before claiming dependable grading.

## Final recorded run

Final calibration run: **18/20 outcomes matched the fixed agent labels**, with **zero accepted false passes**, one unfair follow-up on a complete answer and one operational refusal (`ungrounded_local_pass`) on a correct paraphrase. Thus two complete answers were not passed; the operational count overlaps that total. **Measured evaluation p95 was 75.765 seconds** (maximum 177.672 seconds), so the original under-ten-second target is not met. These are wall-clock measurements from this run, not a representative hardware benchmark. Human review remains incomplete.
