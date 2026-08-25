# Classification, Citation, Compliance, and Refusal Behavior

## Classification
Every incoming user query is classified through a constrained classifier.
Categories include: `FACTUAL`, `ADVICE`, `RECOMMENDATION`, `PREDICTION`, `COMPARISON`.

## Refusal Behavior
If the query falls under a prohibited intent (e.g. `RECOMMENDATION`), the orchestration immediately short-circuits and returns a `POLICY_REFUSAL` status with a fixed template.

## Generation & Compliance
- **Citation**: The renderer appends exactly *one* Groww URL.
- **Compliance Rules**: The answer must contain no more than 3 sentences. No advice language. The final validation step verifies that all facts trace back to the exact passage.
