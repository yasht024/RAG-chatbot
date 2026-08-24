# Evaluation Dataset and Runner Instructions

## Dataset
The dataset is pinned at `tests/evaluation/seed_dataset.json`. It contains factual question types, out-of-bounds questions, and refusal checks for 35 schemes.

## Runner Instructions
To run the automated evaluation:
```bash
python -m pytest tests/evaluation/ -v --html=docs/reports/eval_report.html
```

Metrics tracked:
- Recall@5 for factual questions.
- False Allow rate for prohibited policy classes (must be 0%).
