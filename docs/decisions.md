# Mutual Fund FAQ Assistant - Decision Register & Escalation Rules

## 1. Phase 0 Open Decisions
These decisions must be resolved to establish the engineering boundaries and prevent rework before broad implementation begins (Phase 0).

| ID | Decision | Final Decision Details | Owner | Status | Date |
|---|---|---|---|---|---|
| P0-01 | Decision Register | Created this decision register to track architectural decisions. | Product Owner | **Approved** | 2026-08-23 |
| P0-02 | Source Precedence | 1. Groww Scheme Pages (`groww.in/mutual-funds/...`) 2. Groww Procedure Pages 3. Groww Official Disclosures. | Product + Domain | **Approved** | 2026-08-23 |
| P0-03 | Freshness Thresholds | Notices/Scheme Pages: Daily. Factsheets: Weekly (Daily near release). SID/KIM: Weekly. | Product + Domain | **Approved** | 2026-08-23 |
| P0-04 | Refusal-link & Mixed-intent | Fail closed for mixed intent. Refusal link points to AMFI investor education portal. | Product Owner | **Approved** | 2026-08-23 |
| P0-05 | Direct Growth Default | Default to Direct Growth if omitted. Refuse unsupported options (e.g. Regular IDCW). | Product + Domain | **Approved** | 2026-08-23 |
| P0-06 | Model Provider Config | OpenAI API. `openai/gpt-oss-120b` (gen and class). Zero data retention. | Architecture | **Approved** | 2026-08-23 |
| P0-06b | Embedding Model | `BAAI/bge-large-en-v1.5` (1024 dims). Replaces default 1536 dims. | Architecture | **Approved** | 2026-08-24 |
| P0-07 | Retention Policy | Raw queries/answers: 7 days. Traces/Audit: 30 days. PII redacted before logging. | Security | **Approved** | 2026-08-23 |
| P0-08 | Release Thresholds | Recall@5 >= 95%, Exact Fact Accuracy >= 95%, 100% adherence to rules, 0 false factual. | QA + Engineering | **Approved** | 2026-08-23 |
| P0-09 | User Feedback Storage | Store user thumbs up/down feedback along with query and conversation ID in a local SQLite database for MVP manual review. | Product + Engineering | **Approved** | 2026-09-02 |

## 2. Decision and Escalation Rules
During implementation, work must pause for product, domain, or security review when any of the following conditions are met:

1. **Source Disagreement:** Two current Groww sources disagree and configured precedence does not resolve the fact.
2. **Ambiguous Scope:** A Groww document applies to a scheme but the plan or option scope is unclear.
3. **Missing Dates:** A source lacks a reliable publication or effective date.
4. **Calculations Needed:** A requested fact would require calculation or interpretation (violating the facts-only policy).
5. **New Infrastructure:** A new source domain, document type, or data region is proposed. (OpenAI API for `openai/gpt-oss-120b` is the initial model provider for the MVP).
6. **Privacy Boundary:** A change could expose user input beyond approved retention or processing boundaries.
7. **Release Quality:** A release candidate violates a zero-tolerance gate.

*Note: The team may continue unrelated work while the affected fact, source, or feature remains disabled.*
