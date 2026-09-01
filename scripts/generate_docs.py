import json
import csv
import os


def generate_docs():
    workspace = "."
    data_dir = os.path.join(workspace, "data", "catalog")
    docs_dir = os.path.join(workspace, "docs")

    os.makedirs(os.path.join(docs_dir, "reports"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "policies"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "architecture"), exist_ok=True)
    os.makedirs(os.path.join(docs_dir, "eval"), exist_ok=True)

    with open(os.path.join(data_dir, "schemes.json"), "r") as f:
        schemes = json.load(f)

    with open(os.path.join(data_dir, "sources.json"), "r") as f:
        sources = json.load(f)

    # 1. P2B-DOC-01: README.md
    readme_content = """# Mutual Fund FAQ Assistant

## Overview
A production-ready facts-only AI assistant for HDFC Mutual Fund schemes. It answers objective facts supported by current approved Groww evidence. It strictly refuses advice, recommendations, predictions, and prohibited performance requests.

## Setup and Local Development
1. Install dependencies:
   `pip install -r requirements.txt` (Backend)
   `cd apps/web && npm install` (Frontend)
2. Start local services (Postgres, Redis):
   `docker-compose up -d`
3. Run API:
   `cd services/assistant_api && uvicorn orchestrator:app --reload`
4. Run Web UI:
   `cd apps/web && npm run dev`

## Documentation & Architecture
- [Implementation Plan](docs/implementation-plan.md)
- [Architecture](docs/Architecture.md)
- [Sources Policy](docs/policies/sources_policy.md)
- [Scheme Catalog](docs/reports/scheme_catalog.md)
"""
    with open(os.path.join(workspace, "README.md"), "w") as f:
        f.write(readme_content)

    # 2. P2B-DOC-02: Scheme Catalog
    catalog_md = "# Supported Scheme Catalog\n\n| Scheme ID | Canonical Name | AMC | Category | Groww URL |\n|---|---|---|---|---|\n"
    for s in schemes:
        catalog_md += f"| `{s['scheme_id']}` | {s['canonical_name']} | {s['amc']} | {s['category']} | [Link]({s['groww_url']}) |\n"
    with open(os.path.join(docs_dir, "reports", "scheme_catalog.md"), "w") as f:
        f.write(catalog_md)

    # 3. P2B-DOC-03: Sources Policy
    sources_md = f"""# Approved Sources and Prohibited-Source Policy

## Approved Domains
{chr(10).join(["- " + d for d in sources["allowed_domains"]])}

## Allowed URL Prefixes
{chr(10).join(["- " + d for d in sources["allowed_url_prefixes"]])}

## Prohibited Domains
{chr(10).join(["- " + d for d in sources["prohibited_domains"]])}

### Enforcement
The fetcher automatically rejects any redirect or request to prohibited domains. Evidence validation ensures that citations come exclusively from allowed domains.
"""
    with open(os.path.join(docs_dir, "policies", "sources_policy.md"), "w") as f:
        f.write(sources_md)

    # 4. P2B-DOC-04: Ingestion & Retrieval Design
    ingest_md = """# Ingestion, Chunking, Embedding, and Retrieval Design

## Ingestion
1. **Fetching**: Fetch artifacts (HTML/PDF) idempotently. Generate SHA-256 hashes for deduplication.
2. **Parsing**: Extract structure (headings, tables). For PDFs, parse text and layout mapping.
3. **Chunking**: Sectional boundary preservation. Tokens partitioned by semantic sections (250–500 tokens).

## Embedding
Passages are enriched with `scheme_ids`, `plan`, `option`, and `heading_path`. Embedded using `BGE Large` (1024-dimensional pgvector).

## Retrieval
Uses a hybrid approach (PostgreSQL keyword search + pgvector). Re-ranking favors precise passages (e.g. matched sections/tables) over generic mentions. Hard filters applied to `scheme_id`, `plan`, and `option` before vector search.
"""
    with open(os.path.join(docs_dir, "architecture", "ingestion_retrieval.md"), "w") as f:
        f.write(ingest_md)

    # 5. P2B-DOC-05: Classification & Generation
    class_md = """# Classification, Citation, Compliance, and Refusal Behavior

## Classification
Every incoming user query is classified through a constrained classifier.
Categories include: `FACTUAL`, `ADVICE`, `RECOMMENDATION`, `PREDICTION`, `COMPARISON`.

## Refusal Behavior
If the query falls under a prohibited intent (e.g. `RECOMMENDATION`), the orchestration immediately short-circuits and returns a `POLICY_REFUSAL` status with a fixed template.

## Generation & Compliance
- **Citation**: The renderer appends exactly *one* Groww URL.
- **Compliance Rules**: The answer must contain no more than 3 sentences. No advice language. The final validation step verifies that all facts trace back to the exact passage.
"""
    with open(os.path.join(docs_dir, "architecture", "classification_generation.md"), "w") as f:
        f.write(class_md)

    # 6. P2B-DOC-06: Disclaimer Snippet
    disclaim_md = """# Disclaimer Snippet
The following persistent disclaimer must be displayed in the Chat UI at all times:

`Facts-only. No investment advice.`

### Secondary Text (Footer)
`Responses are generated based on official fund documents. Always verify independently.`
"""
    with open(os.path.join(docs_dir, "policies", "disclaimer_snippet.md"), "w") as f:
        f.write(disclaim_md)

    # 7. P2B-DOC-07: Export Metadata (CSV)
    with open(os.path.join(data_dir, "schemes_export.csv"), "w", newline="") as f:
        if schemes:
            writer = csv.DictWriter(f, fieldnames=schemes[0].keys())
            writer.writeheader()
            for s in schemes:
                writer.writerow(s)

    # 8. P2B-DOC-08: Evaluation Dataset & Runner
    eval_md = """# Evaluation Dataset and Runner Instructions

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
"""
    with open(os.path.join(docs_dir, "eval", "evaluation_dataset.md"), "w") as f:
        f.write(eval_md)

    # 9. P2B-DOC-09: Limitations
    limitations_md = """# Known Limitations and Controlled Failure Behavior

## Known Limitations
1. **Document Types**: The system only parses HTML factsheets and natively digital PDFs. Scanned PDFs without OCR confidence >90% will fall back to `INSUFFICIENT_EVIDENCE`.
2. **Tabular Reasoning**: Extremely complex cross-table calculations are not supported; the system pulls scalar facts directly.

## Controlled Failure States
- **Missing Evidence**: Returns `INSUFFICIENT_EVIDENCE`. No hallucinations allowed.
- **Ambiguity**: Returns `AMBIGUOUS_SCHEME` if a query matches multiple schemes equally.
- **Source Conflict**: If two valid sources disagree on a scalar fact, returns `SOURCE_CONFLICT`.
"""
    with open(os.path.join(docs_dir, "reports", "limitations.md"), "w") as f:
        f.write(limitations_md)

    print("Successfully generated all Workstream F documentation!")


if __name__ == "__main__":
    generate_docs()
