# Mutual Fund FAQ Assistant - Phase-Wise Implementation Plan

## Document Control

| Field | Value |
| --- | --- |
| Project | Mutual Fund FAQ Assistant |
| Initial AMC | HDFC Mutual Fund / HDFC Asset Management Company (Groww) |
| Document type | Phase-wise implementation plan |
| Status | Proposed for execution |
| Requirements source | `docs/problemStatement.md` |
| Architecture source | `docs/Architecture.md` |
| Initial scope | 35 HDFC Mutual Fund schemes |
| Planning baseline | 23 August 2026 |

## 1. Purpose

This plan converts the approved product requirements and proposed architecture into an executable delivery sequence. It defines phase outcomes, work packages, dependencies, ownership roles, implementation tasks, deliverables, verification activities, and release gates.

The plan is intentionally evidence-first. Corpus governance, policy rules, and evaluation fixtures are built before broad answer generation so that later RAG quality can be measured against stable source and safety contracts.

## 2. Delivery Objective

Deliver a production-ready facts-only assistant that:

- Covers all 35 in-scope HDFC Mutual Fund schemes.
- Answers only objective facts supported by current approved Groww evidence.
- Resolves scheme names and approved aliases correctly.
- Refuses advice, recommendations, ranking, prediction, and prohibited performance requests.
- Returns no more than three answer sentences.
- Returns exactly one Groww source link for every factual answer.
- Uses the cited evidence's effective or publication date in the last-updated footer.
- Fails closed when evidence is missing, ambiguous, stale, conflicting, or invalid.
- Can refresh, validate, publish, monitor, and roll back corpus versions safely.

## 3. Planning Assumptions

### 3.1 Team Model

The effort bands in this plan assume a small cross-functional team:

| Role | Suggested allocation | Primary responsibilities |
| --- | ---: | --- |
| Product owner | 0.5 FTE | Scope, policy decisions, acceptance, user experience |
| Mutual-fund domain reviewer | 0.25-0.5 FTE | Source precedence, fact interpretation, conflict review |
| Backend/RAG engineers | 2 FTE | API, orchestration, retrieval, validation, generation |
| Data/ingestion engineer | 1 FTE | Fetching, parsing, metadata, chunking, indexing |
| Frontend engineer | 1 FTE during MVP | Chat UI, integration, accessibility |
| QA/evaluation engineer | 1 FTE | Test automation, evaluation corpus, release gates |
| Platform/SRE engineer | 0.25-0.5 FTE | Environments, CI/CD, observability, operations |
| Security/privacy reviewer | Fractional | Threat model, data handling, production review |

One person may cover multiple roles. If the team is smaller, preserve the phase dependency order and extend the schedule rather than removing validation gates.

### 3.2 Effort Model

- One sprint is assumed to be two weeks.
- Phase estimates are planning ranges, not delivery commitments.
- Phase 1 ingestion work and Phase 1 policy work may run in parallel after Phase 0 contracts are approved.
- The MVP is expected to require approximately 7-9 sprints for this team model.
- Production hardening is expected to require another 2-3 sprints.
- Phase 4 is an ongoing controlled-expansion track, not part of the initial production commitment.

### 3.3 Technical Baseline

The implementation follows the replaceable reference stack from the architecture:

| Capability | Initial implementation |
| --- | --- |
| Web client | React/Next.js with TypeScript |
| API and orchestration | Python with FastAPI and Pydantic |
| Relational metadata | PostgreSQL |
| Vector retrieval | PostgreSQL with pgvector initially |
| Keyword retrieval | PostgreSQL full-text search initially |
| Immutable originals | Versioned S3-compatible object storage |
| Cache | Redis, introduced during hardening |
| Background processing | Managed queue or equivalent worker queue |
| Telemetry | OpenTelemetry-compatible metrics, logs, and traces |
| Local development | Containers for PostgreSQL, object storage, and optional Redis |

Technology substitutions are acceptable when they preserve the architecture's contracts, trust boundaries, auditability, and release gates.

## 4. Delivery Principles

1. **Fail closed:** uncertainty produces a controlled refusal, not a best guess.
2. **Policy outside prompts:** financial-safety and response-contract rules are enforced in application code.
3. **Evidence before generation:** a model receives only validated, bounded evidence.
4. **One source of truth:** the selected evidence owns the citation and last-updated date.
5. **Immutable evidence:** raw source versions are retained and addressed by content hash.
6. **Version everything:** corpus, policies, prompts, models, parsers, and evaluations are independently versioned.
7. **Thin vertical slices:** prove one complete path before expanding coverage.
8. **No live browsing in serving:** online answers use the approved indexed corpus.
9. **Automate objective checks:** sentence count, citation count, domain, date, and response type are deterministic gates.
10. **Release quality over answer rate:** never improve apparent coverage by weakening evidence requirements.

## 5. Phase Map and Dependencies

```mermaid
flowchart LR
    P0[Phase 0: Decisions and foundation] --> P1[Phase 1: Corpus and policy foundation]
    P1 --> P2A[Phase 2A: End-to-end vertical slice]
    P2A --> P2B[Phase 2B: Full facts-only MVP]
    P2B --> P3A[Phase 3A: Quality and resilience hardening]
    P3A --> P3B[Phase 3B: Production readiness and rollout]
    P3B --> P4[Phase 4: Controlled expansion]
```

| Phase | Outcome | Indicative effort | Release significance |
| --- | --- | ---: | --- |
| Phase 0 | Decisions, contracts, repository, environments, seed evaluation | 1 sprint | Development-ready baseline |
| Phase 1 | Governed corpus pipeline, scheme registry, classifier, refusal policy | 3-4 sprints | Foundation exit gate |
| Phase 2A | Thin end-to-end answer path on representative schemes and facts | 1 sprint | Architecture proof |
| Phase 2B | All required MVP facts, 35 schemes, API, UI, compliance | 2-3 sprints | Feature-complete MVP |
| Phase 3A | Conflict, security, resilience, accessibility, quality tuning | 1-2 sprints | Release candidate |
| Phase 3B | Operational readiness, canary, production rollout | 1 sprint | Initial production release |
| Phase 4 | Approved plans, options, schemes, AMCs, and languages | Ongoing | Post-MVP growth |

## 6. Status and Tracking Conventions

Use the following task status values in the delivery tracker:

| Status | Meaning |
| --- | --- |
| Not started | No implementation activity has begun |
| In progress | Actively being implemented |
| Blocked | Cannot proceed because a named dependency or decision is unresolved |
| In review | Code, data, domain, security, or product review is in progress |
| Complete | Acceptance evidence exists and the phase owner has accepted the task |

Priority values:

- `P0`: Required to preserve safety, correctness, or basic operability.
- `P1`: Required for the initial production release.
- `P2`: Valuable after MVP or when capacity permits.

Task IDs remain stable even when tasks move between sprints.

## 7. Cross-Cutting Definition of Done

Every implementation task is complete only when applicable conditions are met:

- Code is reviewed and merged through the standard CI pipeline.
- Unit and integration tests cover normal, boundary, and failure behavior.
- Schemas and externally consumed contracts are documented.
- Logs and traces contain request IDs but no prohibited sensitive values.
- Metrics exist for new critical paths and failure outcomes.
- Configuration is versioned and environment-specific values are externalized.
- Failure behavior is explicit and fail-closed where evidence or policy is involved.
- Documentation and runbooks are updated.
- Relevant evaluation cases pass against a pinned corpus manifest.
- Domain review is recorded for source interpretation or extracted financial facts.

## 8. Phase 0 - Decisions and Engineering Foundation

### 8.1 Goal

Remove decisions that can cause rework, establish engineering boundaries, and make the repository capable of supporting repeatable implementation and evaluation.

### 8.2 Entry Criteria

- Product problem statement and architecture are available.
- Product, engineering, and domain-review owners are identified.
- Initial cloud, model, and source-access constraints can be discussed.

### 8.3 Work Packages

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P0-01 | P0 | Create a decision register for the ten open architecture decisions | Product owner | None | Each decision has owner, due date, options, and status |
| P0-02 | P0 | Approve source precedence by fact type | Product + domain reviewer | P0-01 | Signed source-selection matrix |
| P0-03 | P0 | Define freshness thresholds by source and fact type | Product + domain reviewer | P0-01 | Versioned freshness-policy configuration |
| P0-04 | P0 | Decide refusal-link and mixed-intent behavior | Product owner | P0-01 | Approved policy examples and reason codes |
| P0-05 | P0 | Confirm Direct Growth default and treatment of unsupported plans/options | Product + domain reviewer | P0-01 | Resolution-policy decision recorded |
| P0-06 | P0 | Select OpenAI API (`openai/gpt-oss-120b`) model provider and data-processing settings | Architecture + security | P0-01 | Approved provider and data-flow record |
| P0-07 | P0 | Define raw query, answer, trace, and audit retention | Security + privacy + product | P0-01 | Approved retention schedule |
| P0-08 | P0 | Agree release thresholds and service-level objectives | Product + engineering + QA | P0-01 | Versioned release-gate configuration |
| P0-09 | P0 | Scaffold repository and module boundaries | Engineering lead | Architecture | Buildable repository skeleton |
| P0-10 | P0 | Add local development stack | Platform engineer | P0-09 | Documented one-command local startup |
| P0-11 | P0 | Configure formatting, linting, type checks, tests, and pre-commit hooks | Engineering lead | P0-09 | CI rejects non-conforming changes |
| P0-12 | P0 | Establish development, staging, and production configuration model | Platform engineer | P0-06, P0-09 | Versioned config schemas; no secrets in repository |
| P0-13 | P0 | Define API, evidence, response, and audit JSON schemas | Backend engineer | Architecture | Reviewed schema package with contract tests |
| P0-14 | P0 | Define error taxonomy and terminal response states | Backend + product | P0-04, P0-13 | Approved reason codes and renderer contract |
| P0-15 | P0 | Create seed evaluation format and first 30-50 cases | QA + domain reviewer | P0-02, P0-04, P0-05 | Versioned dataset covering answer and refusal paths |
| P0-16 | P1 | Create initial threat model and data-flow diagram | Security + engineering | P0-06, P0-13 | Reviewed threat model with assigned mitigations |
| P0-17 | P1 | Define observability naming and request-correlation standard | Platform + backend | P0-13 | Trace and metric naming document |
| P0-18 | P1 | Create architecture-decision record template and first seven ADRs | Engineering lead | Architecture | ADRs committed and linked from README |

### 8.4 Proposed Repository Layout

```text
apps/
  web/                         # Chat UI
services/
  assistant_api/               # FastAPI application and orchestrator
workers/
  ingestion/                   # Discovery, fetch, parse, enrich, index
packages/
  contracts/                   # Shared request, evidence, response schemas
  policy/                      # Classification and compliance rules
  retrieval/                   # Search, fusion, reranking interfaces
  evaluation/                  # Dataset schema, runners, reports
data/
  catalog/                     # Versioned scheme and source registries
  fixtures/                    # Approved parser and test fixtures
infra/
  local/                       # Local containers and bootstrap
  environments/               # Deployment definitions by environment
tests/
  unit/
  integration/
  end_to_end/
  evaluation/
docs/
  problemStatement.md
  Architecture.md
  implementation-plan.md
```

The exact names may change, but the source registry, scheme catalog, policy rules, and evaluation assets must remain independently versioned and reviewable.

### 8.5 Phase Deliverables

- Decision register and approved high-risk policy decisions.
- Buildable repository skeleton.
- Local development environment.
- CI quality pipeline.
- Versioned contracts and error taxonomy.
- Seed evaluation dataset.
- Threat model and data-handling baseline.

### 8.6 Exit Gate

Phase 0 is complete when:

- No unresolved decision blocks schema, ingestion, classification, or source validation work.
- The repository builds and tests in CI from a clean checkout.
- Local services start with documented commands.
- API and evidence contracts are accepted by backend, data, frontend, and QA owners.
- Seed evaluation cases run through a placeholder evaluator and produce a report.
- Security confirms that no personal or transaction data is required for the MVP.

## 9. Phase 1 - Corpus and Policy Foundation

### 9.1 Goal

Build the governed knowledge foundation and query-policy boundary required for a safe RAG implementation. At the end of this phase, Groww documents can be discovered, fetched, parsed, versioned, validated, and published to a staging index; user queries can be classified and refused correctly even before factual answer generation is complete.

### 9.2 Entry Criteria

- Phase 0 exit gate has passed.
- Source precedence, freshness, plans/options, and refusal policies have approved versions.
- Groww source access and usage constraints are known.

### 9.3 Workstream A - Scheme and Source Governance

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P1-GOV-01 | P0 | Define canonical scheme, alias, source, document, passage, fact, conflict, and manifest tables | Data engineer | P0-13 | Reviewed database migrations and data dictionary |
| P1-GOV-02 | P0 | Assign stable IDs to all 35 schemes | Data engineer + domain reviewer | P1-GOV-01 | Registry has exactly 35 active in-scope records |
| P1-GOV-03 | P0 | Populate canonical names, categories, Direct/Growth defaults, and Groww identity references | Data engineer | P1-GOV-02 | Schema validation and domain review pass |
| P1-GOV-04 | P0 | Build curated alias registry with provenance and validity dates | Domain reviewer + data engineer | P1-GOV-02 | Alias tests cover historical and ambiguous names |
| P1-GOV-05 | P0 | Create approved organization, domain, document-type, and discovery-source registry | Data engineer + security | P0-02 | Fetcher-readable allowlist with review metadata |
| P1-GOV-06 | P0 | Encode fact-type source precedence as configuration | Backend + domain reviewer | P0-02, P1-GOV-05 | Policy tests cover every required fact type |
| P1-GOV-07 | P0 | Encode freshness thresholds and stale behavior | Backend + domain reviewer | P0-03 | Boundary-date tests pass |
| P1-GOV-08 | P1 | Add registry validation CLI and CI checks | Data engineer | P1-GOV-02 through P1-GOV-07 | Invalid aliases, domains, and dates fail CI |
| P1-GOV-09 | P1 | Create scheme/fact/source coverage report | Data engineer + QA | P1-GOV-02, P1-GOV-05 | Machine-readable and human-readable reports |

### 9.4 Workstream B - Ingestion Pipeline

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P1-ING-01 | P0 | Implement source scheduler and idempotent job model | Data engineer | P1-GOV-05 | Repeat scheduling does not duplicate source versions |
| P1-ING-02 | P0 | Implement allowlisted fetcher with redirect, content-type, size, timeout, and rate controls | Data engineer + security | P1-ING-01 | Negative security and redirect tests pass |
| P1-ING-03 | P0 | Persist original bytes, response metadata, final URL, and SHA-256 hash | Data engineer | P1-ING-02 | Fetched artifacts are immutable and deduplicated |
| P1-ING-04 | P0 | Implement HTML extraction with heading, table, link, and date preservation | Data engineer | P1-ING-03 | Golden HTML fixture tests pass |
| P1-ING-05 | P0 | Implement PDF text and layout extraction with page mapping | Data engineer | P1-ING-03 | Golden digital-PDF fixture tests pass |
| P1-ING-06 | P1 | Add OCR fallback and confidence capture | Data engineer | P1-ING-05 | Scanned fixture works; low confidence is quarantined |
| P1-ING-07 | P0 | Normalize text while preserving source text, numeric values, footnotes, and tables | Data engineer | P1-ING-04, P1-ING-05 | Normalization snapshot tests pass |
| P1-ING-08 | P0 | Detect publication and effective dates with provenance | Data engineer + domain reviewer | P1-ING-07 | Date extraction evaluation meets approved threshold |
| P1-ING-09 | P0 | Map documents to scheme, plan, option, scope, and document type | Data engineer | P1-GOV-04, P1-ING-07 | Uncertain mappings are quarantined, never guessed |
| P1-ING-10 | P0 | Implement structure-aware chunking for prose and tables | Data engineer | P1-ING-07, P1-ING-09 | Headers, qualifiers, rows, and footnotes stay attached |
| P1-ING-11 | P1 | Tag passages with supported fact types | Data/RAG engineer | P1-ING-10 | Fact-type tagging report available |
| P1-ING-12 | P0 | Generate embeddings with model/version/hash metadata | RAG engineer | P1-ING-10 | Deterministic reprocessing and version tracking work |
| P1-ING-13 | P0 | Populate staging keyword and vector indexes | RAG engineer | P1-ING-10, P1-ING-12 | All approved passages are searchable by manifest |
| P1-ING-14 | P0 | Implement quarantine queue and reason codes | Data engineer | P1-ING-02 through P1-ING-13 | Failed items are inspectable and excluded from serving |
| P1-ING-15 | P0 | Build automated ingestion quality checks | QA + data engineer | P1-ING-13, P1-ING-14 | Bad dates, domains, mappings, hashes, and empty text block publication |
| P1-ING-16 | P1 | Implement content-change and duplicate detection | Data engineer | P1-ING-03 | Unchanged content avoids unnecessary re-indexing |
| P1-ING-17 | P1 | Add retry, backoff, and dead-letter handling | Data engineer + platform | P1-ING-01, P1-ING-02 | Transient-failure tests and dead-letter alert pass |

### 9.4.1 Structure-Aware Chunking Strategy for Processed Data

The chunker (`workers/ingestion/chunker.py`) consumes the clean, normalized JSON artifacts in `data/processed/<scheme_id>.json` rather than raw HTML to ensure high retrieval quality and exact fact binding:

1. **Input Source:** Cleaned intermediate artifacts in `data/processed/` containing `scheme_id`, `canonical_url`, `document_title`, `sections`, and `extracted_facts`.
2. **Sectional Boundary Preservation:** Chunks are partitioned by semantic sections (250–500 tokens). Headings (e.g. `[Fund Overview & Investment Objective]`, `[Key Scheme Facts]`) are preserved in the passage text and metadata.
3. **Automated Fact-Type Tagging:** Passages are cross-referenced with `extracted_facts` and tagged with exact fact types (`EXPENSE_RATIO`, `EXIT_LOAD`, `MINIMUM_SIP`, `BENCHMARK`, `RISKOMETER`, `FUND_MANAGER`, `LOCK_IN`).
4. **Atomic Fact Preservation:** Multi-attribute fact blocks (e.g. Exit load redemption conditions, Expense Ratio percentages, SIP minimums) are kept atomic within the passage to prevent qualifying clauses from being split.
5. **Passage Metadata Enrichment:** Each passage is stored with `scheme_ids`, `plan="Direct"`, `option="Growth"`, `heading_path`, `extraction_confidence=1.0`, and a 1024-dimensional `pgvector` embedding (BGE Large).

### 9.5 Representative-Source Rollout Order

Do not ingest all sources at once. Prove each parser and metadata path in this order:

1. One Groww scheme page for a diversified equity scheme (e.g., HDFC Mid Cap Fund - Direct Growth).
2. One Groww scheme page for an index fund (e.g., HDFC NIFTY 50 Index Fund - Direct Growth).
3. One Groww scheme page for an ELSS tax saver fund (e.g., HDFC ELSS Tax Saver Fund - Direct Growth).
4. One Groww AMC-level account-statement or capital-gains procedure page.
5. Expand to all 35 Groww scheme URLs.

Each step adds parser fixtures and metadata assertions before expansion continues.

### 9.6 Workstream C - Query Policy and Privacy Boundary

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P1-POL-01 | P0 | Implement normalized query and classification schemas | Backend engineer | P0-13 | Schema contract tests pass |
| P1-POL-02 | P0 | Implement deterministic rules for advice, recommendation, ranking, prediction, comparison, calculation, and transaction intent | Backend + QA | P0-04 | Critical policy suite passes with no false allows |
| P1-POL-03 | P0 | Implement constrained model classifier for linguistic variation | RAG engineer | P1-POL-01 | Only allowed enum/schema outputs accepted |
| P1-POL-04 | P0 | Implement conservative policy merger | Backend engineer | P1-POL-02, P1-POL-03 | Prohibited class wins every disagreement test |
| P1-POL-05 | P0 | Implement fact-type and scheme/AMC scope classification | RAG engineer | P1-POL-03 | Required factual categories meet target accuracy |
| P1-POL-06 | P0 | Implement sensitive-data detection and redaction boundary | Backend + security | P0-07 | PAN, Aadhaar, bank, OTP, email, phone, and credential tests pass |
| P1-POL-07 | P0 | Implement fixed refusal templates by reason code | Backend + product | P0-04, P0-14 | Product-approved snapshots for every refusal type |
| P1-POL-08 | P1 | Add classifier confidence thresholds and low-confidence behavior | RAG engineer + product | P1-POL-03, P1-POL-04 | Low confidence never defaults to factual retrieval |
| P1-POL-09 | P1 | Instrument classification outcome, latency, and policy version | Backend + platform | P0-17, P1-POL-04 | Dashboard shows redacted aggregate metrics |

### 9.7 Workstream D - Scheme and Intent Resolution

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P1-RES-01 | P0 | Implement exact canonical-name resolution | Backend engineer | P1-GOV-02 | All 35 canonical-name tests pass |
| P1-RES-02 | P0 | Implement curated alias resolution | Backend engineer | P1-GOV-04 | All approved aliases resolve correctly |
| P1-RES-03 | P0 | Add constrained fuzzy matching against the registry | Backend engineer | P1-RES-01, P1-RES-02 | Threshold and typo tests avoid wrong-scheme answers |
| P1-RES-04 | P0 | Implement ambiguity detection and clarification result | Backend + product | P1-RES-03, P0-14 | Multi-match tests return `AMBIGUOUS_SCHEME` |
| P1-RES-05 | P0 | Resolve plan, option, fact type, requested date, and document type | Backend engineer | P0-05, P1-POL-05 | Resolution contract tests pass |
| P1-RES-06 | P0 | Apply Direct Growth default only when permitted | Backend + domain reviewer | P0-05, P1-RES-05 | Explicit unsupported plan is never overwritten |
| P1-RES-07 | P1 | Cache registry and alias data by version | Backend engineer | P1-RES-01 through P1-RES-06 | Version change invalidates in-memory cache |

### 9.8 Workstream E - Evaluation Foundation

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P1-EVAL-01 | P0 | Expand dataset across all required question and refusal types | QA + domain reviewer | P0-15 | Minimum agreed cases per fact/policy category |
| P1-EVAL-02 | P0 | Add all 35 canonical names and curated aliases | QA | P1-GOV-04 | Scheme resolution suite has full scheme coverage |
| P1-EVAL-03 | P0 | Add stale, conflicting, wrong-plan, wrong-option, and unsupported evidence cases | QA + domain reviewer | P1-GOV-06, P1-GOV-07 | Negative evidence cases are versioned |
| P1-EVAL-04 | P0 | Build classifier and resolver evaluation runners | QA + RAG engineer | P1-POL-04, P1-RES-06 | Reproducible reports include per-class metrics |
| P1-EVAL-05 | P1 | Add prompt-injection and sensitive-data cases | QA + security | P1-POL-06 | Adversarial suite runs in CI or nightly pipeline |
| P1-EVAL-06 | P1 | Create parser quality fixtures and visual review checklist | QA + data engineer | P1-ING-04 through P1-ING-10 | Representative HTML/PDF/table fixtures approved |

### 9.9 Phase Deliverables

- Canonical metadata for all 35 schemes.
- Curated alias and source registries.
- Versioned fact-type source precedence and freshness policies.
- Immutable source storage and relational metadata model.
- HTML, PDF, and OCR-aware ingestion pipeline.
- Structure-aware chunks and staging indexes.
- Query classifier, privacy guard, refusal templates, and scheme resolver.
- Expanded evaluation dataset and automated evaluation runners.
- Coverage, ingestion, and classification dashboards.

### 9.10 Exit Gate

Phase 1 is complete when:

- The registry contains exactly the 35 approved schemes with reviewed metadata and aliases.
- All corpus records originate from an approved Groww source.
- Redirects to prohibited domains are rejected.
- Representative scheme pages, factsheets, SID, KIM, notices/addendums, and AMC procedure pages parse successfully.
- Every indexed passage has document, source, date, scope, and location provenance.
- Quarantined documents cannot enter the serving index.
- Critical advisory and performance-comparison tests have zero false factual classifications.
- Sensitive-data tests prove raw detected values do not reach retrieval, generation, or standard logs.
- Canonical scheme resolution is 100% on the evaluation set.
- A versioned staging corpus manifest can be built repeatedly from pinned fixtures.

## 10. Phase 2A - End-to-End Vertical Slice

### 10.1 Goal

Prove the complete online architecture with a deliberately narrow scope before expanding all fact types and schemes. This phase should expose contract or data-model problems while the cost of change is still low.

### 10.2 Slice Scope

Use three structurally different schemes:

- HDFC Mid Cap Fund - Direct Growth.
- HDFC ELSS Tax Saver Fund - Direct Growth.
- HDFC NIFTY 50 Index Fund - Direct Growth.

Support three scalar facts plus one refusal path:

- Minimum SIP amount.
- Benchmark index.
- ELSS lock-in period.
- Investment recommendation refusal.

The selected values must come from actual approved corpus evidence and be reviewed by the domain owner. Values shown in examples are never treated as truth unless the current source confirms them.

### 10.3 Work Packages

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2A-01 | P0 | Implement retrieval interface and metadata hard filters | RAG engineer | Phase 1 | Wrong source/scheme/plan/option candidates cannot pass |
| P2A-02 | P0 | Implement keyword search | RAG engineer | P2A-01 | Exact scheme, heading, and value queries retrieve gold passages |
| P2A-03 | P0 | Implement vector search | RAG engineer | P2A-01 | Paraphrases retrieve gold passages |
| P2A-04 | P0 | Implement rank fusion and initial reranking | RAG engineer | P2A-02, P2A-03 | Retrieval report shows ranked gold evidence |
| P2A-05 | P0 | Implement source, scope, date, status, hash, and supersession validation | Backend + data engineer | P1-GOV-06, P1-GOV-07, P2A-04 | Invalid candidates return named evidence failures |
| P2A-06 | P0 | Implement bounded context builder | RAG engineer | P2A-05 | Context contains only selected evidence and provenance |
| P2A-07 | P0 | Extract and validate three slice fact types | Data/RAG engineer | P2A-05 | Structured facts bind to passage offsets |
| P2A-08 | P0 | Implement deterministic scalar answer templates | Backend engineer | P2A-07 | Templates generate no unsupported text |
| P2A-09 | P0 | Implement compliance checks for sentence count, citation count/domain, date, and policy class | Backend + QA | P0-13, P2A-08 | Mutation tests fail each intentionally broken response |
| P2A-10 | P0 | Implement renderer-owned source and last-updated footer | Backend engineer | P2A-05, P2A-09 | Exactly one selected Groww URL is rendered |
| P2A-11 | P0 | Implement orchestrator state machine and terminal states | Backend engineer | P1-POL-07, P1-RES-06, P2A-01 through P2A-10 | Every request follows mandatory state transitions |
| P2A-12 | P0 | Expose `POST /v1/questions` and health endpoints | Backend engineer | P2A-11 | API contract and integration tests pass |
| P2A-13 | P0 | Create minimal internal test page or API client | Frontend/backend | P2A-12 | Reviewers can execute the slice end to end |
| P2A-14 | P0 | Add request-level trace with policy, index, prompt, and model versions | Platform + backend | P0-17, P2A-11 | One trace explains every decision and evidence selection |
| P2A-15 | P0 | Build end-to-end evaluation for the slice | QA | P2A-12 | Answer, source, date, and refusal assertions pass |

### 10.4 Vertical-Slice Acceptance Examples

For every supported slice query:

- Classification is factual and the expected fact type is selected.
- The intended scheme, Direct plan, and Growth option are resolved.
- The gold passage appears in retrieval results.
- Evidence validation selects one applicable Groww document.
- The answer value is bound to the selected passage.
- The response body has one to three sentences.
- The renderer emits exactly one Groww link.
- The footer date matches the cited evidence.

For recommendation queries:

- Retrieval and generation are not invoked.
- A product-approved refusal reason and template are returned.
- No fund is implicitly favored.

### 10.5 Exit Gate

Phase 2A is complete when:

- All three representative schemes answer the scoped facts correctly from reviewed evidence.
- The recommendation request is refused before retrieval.
- Deliberately stale, wrong-plan, wrong-scheme, unapproved-domain, and conflicting candidates fail closed.
- Removing evidence causes `INSUFFICIENT_EVIDENCE`, not a model-generated guess.
- Altering the draft to include a second link, wrong date, fourth sentence, or advice fails compliance validation.
- The complete decision trace can be replayed against the pinned corpus manifest.

## 11. Phase 2B - Full Facts-Only MVP

### 11.1 Goal

Expand the proven slice across all in-scope schemes and required question types, add constrained language generation where templates are insufficient, and deliver the production-shaped API and chat experience.

### 11.2 Workstream A - Retrieval Expansion

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-RET-01 | P0 | Tune metadata filters and retrieval across all 35 schemes | RAG engineer | Phase 2A | Scheme-level retrieval report meets target |
| P2B-RET-02 | P0 | Add document-type routing by fact type | RAG engineer + domain reviewer | P1-GOV-06, P2A-04 | Each fact searches eligible document classes |
| P2B-RET-03 | P0 | Add date, page, section, table, and heading ranking features | RAG engineer | P2A-04 | Relevant precise passages rank above generic mentions |
| P2B-RET-04 | P0 | Add AMC-level retrieval path for process questions | RAG engineer | P2B-RET-02 | Scheme filter is not incorrectly required |
| P2B-RET-05 | P0 | Implement factual single-performance-value routing | RAG + policy engineers | P2B-RET-02 | Exact Groww factsheet values may pass; comparisons/calculations are blocked |
| P2B-RET-06 | P1 | Add retrieval diagnostics endpoint for authorized operators | Backend engineer | P2B-RET-01 | Operators can inspect ranked passage IDs without public exposure |
| P2B-RET-07 | P0 | Complete retrieval evaluation and error analysis | QA + RAG engineer | P2B-RET-01 through P2B-RET-05 | Recall@5 and correct-document metrics meet release target |

### 11.3 Workstream B - Fact Extraction and Evidence Validation

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-EVD-01 | P0 | Add expense-ratio extraction with plan/option binding | Data/RAG engineer | P2A-07 | Numeric value and qualifiers bind to source offsets |
| P2B-EVD-02 | P0 | Add exit-load extraction with conditions and effective date | Data/RAG engineer + domain reviewer | P2A-07 | Conditional clauses remain attached |
| P2B-EVD-03 | P0 | Add minimum SIP and lump-sum extraction | Data/RAG engineer | P2A-07 | Amount, frequency, and exceptions are represented |
| P2B-EVD-04 | P0 | Add benchmark and riskometer extraction | Data/RAG engineer | P2A-07 | Scheme and benchmark riskometers cannot be confused |
| P2B-EVD-05 | P0 | Add lock-in, fund manager, inception date, plan, and option extraction | Data/RAG engineer | P2A-07 | Facts have explicit scope and source binding |
| P2B-EVD-06 | P0 | Add Groww factsheet-location evidence type | Backend + data engineer | P2B-RET-02 | Returned link is official and specific |
| P2B-EVD-07 | P0 | Add source validation for AMC procedures | Backend engineer | P2B-RET-04 | Procedure answers use current AMC-level evidence |
| P2B-EVD-08 | P0 | Add fact-level conflict detection for overlapping active evidence | Backend + data engineer | P2A-05 | Unresolved values return `SOURCE_CONFLICT` |
| P2B-EVD-09 | P0 | Apply source precedence and regulatory override rules | Backend + domain reviewer | P1-GOV-06, P2B-EVD-08 | Decision tests cover HDFC, Groww, and Groww precedence |
| P2B-EVD-10 | P0 | Complete evidence-validation negative suite | QA | P2B-EVD-01 through P2B-EVD-09 | Stale, superseded, absent, and incompatible evidence is blocked |

### 11.4 Workstream C - Answer Generation and Compliance

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-ANS-01 | P0 | Add deterministic templates for all scalar fact types | Backend + product | P2B-EVD-01 through P2B-EVD-06 | Snapshot tests cover each fact type |
| P2B-ANS-02 | P0 | Implement constrained generator schema | RAG engineer | P0-13, P2A-06 | Invalid model output cannot enter rendering |
| P2B-ANS-03 | P0 | Create evidence-only prompt for investment-objective summaries | RAG + domain reviewer | P2B-ANS-02 | Output remains faithful and concise in evaluation |
| P2B-ANS-04 | P0 | Create evidence-only prompt for account and capital-gains procedures | RAG + product | P2B-ANS-02, P2B-EVD-07 | Steps are source-supported and request no credentials |
| P2B-ANS-05 | P0 | Add explicit insufficient-evidence return from generator | RAG engineer | P2B-ANS-02 | Missing values never trigger model completion from memory |
| P2B-ANS-06 | P0 | Implement semantic claim-to-evidence validation | RAG + QA | P2B-ANS-01 through P2B-ANS-04 | Unsupported additions are rejected |
| P2B-ANS-07 | P0 | Complete deterministic response-contract validator | Backend + QA | P2A-09 | All sentence, source, date, and policy mutations fail |
| P2B-ANS-08 | P1 | Implement one bounded repair attempt | RAG engineer | P2B-ANS-06, P2B-ANS-07 | Second failure always produces controlled refusal |
| P2B-ANS-09 | P0 | Finalize renderer for answer and refusal response types | Backend + product | P2B-ANS-07, P0-04 | Product-approved API and display snapshots |
| P2B-ANS-10 | P0 | Add no-LLM fallback for validated structured facts | Backend engineer | P2B-ANS-01 | Scalar answers remain available during generator failure |

### 11.5 Workstream D - API and Orchestration

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-API-01 | P0 | Expand orchestrator to all terminal states and timeouts | Backend engineer | P2A-11 | State-machine tests cover every transition |
| P2B-API-02 | P0 | Implement API request size, schema, locale, and idempotency behavior | Backend engineer | P2A-12 | Contract and malformed-request tests pass |
| P2B-API-03 | P0 | Add rate limiting and abuse controls | Platform + backend | P2B-API-02 | Load and limit tests pass |
| P2B-API-04 | P0 | Implement live, ready, and corpus health endpoints | Backend + platform | P2B-API-01 | Readiness fails when mandatory evidence services fail |
| P2B-API-05 | P0 | Implement redacted error handling and correlation IDs | Backend engineer | P0-17 | No stack trace or sensitive content reaches clients |
| P2B-API-06 | P1 | Publish OpenAPI and typed frontend client | Backend + frontend | P2B-API-02 | CI checks client/server contract compatibility |
| P2B-API-07 | P0 | Add API integration test suite with pinned corpus | QA + backend | P2B-API-01 through P2B-API-06 | All terminal response types are asserted |

### 11.6 Workstream E - Chat User Experience

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-UI-01 | P0 | Build responsive chat shell | Frontend engineer | P2B-API-06 | Desktop and mobile flows render correctly |
| P2B-UI-02 | P0 | Add required welcome message and example questions | Frontend + product | P2B-UI-01 | Copy matches approved requirements |
| P2B-UI-03 | P0 | Display persistent `Facts-only. No investment advice.` disclaimer | Frontend engineer | P2B-UI-01 | Visible before and during conversation |
| P2B-UI-04 | P0 | Render factual answer, exactly one source, and last-updated date | Frontend engineer | P2B-ANS-09, P2B-API-06 | UI uses server fields without reconstructing citations |
| P2B-UI-05 | P0 | Render refusal, insufficient evidence, ambiguity, conflict, and unavailable states | Frontend + product | P2B-ANS-09 | State-specific UX snapshot tests pass |
| P2B-UI-06 | P0 | Prevent accidental collection of account or credential fields | Frontend + security | P2B-UI-01 | UI contains no personal-data form controls |
| P2B-UI-07 | P1 | Add loading, retry, and source-link failure behavior | Frontend engineer | P2B-UI-04, P2B-UI-05 | Network-failure tests pass |
| P2B-UI-08 | P0 | Complete keyboard, screen-reader, contrast, and responsive checks | Frontend + QA | P2B-UI-01 through P2B-UI-07 | Automated checks and manual accessibility review pass |

### 11.7 Workstream F - Documentation and Expected Deliverables

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P2B-DOC-01 | P0 | Create project README with overview and setup | Engineering | Phase 2B implementation | Clean-checkout setup is verified |
| P2B-DOC-02 | P0 | Document selected AMC and all 35 schemes with Groww reference links | Product + engineering | P1-GOV-03 | README and registry agree |
| P2B-DOC-03 | P0 | Document approved sources and prohibited-source policy | Domain reviewer | P1-GOV-05 | Source policy is explicit |
| P2B-DOC-04 | P0 | Document ingestion, chunking, embedding, and retrieval design | Data/RAG engineer | Phase 1, P2B-RET tasks | Documentation matches deployed versions |
| P2B-DOC-05 | P0 | Document classification, citation, compliance, and refusal behavior | Backend + product | P2B-ANS tasks | Examples match contract tests |
| P2B-DOC-06 | P0 | Publish disclaimer snippet | Product owner | P2B-UI-03 | Exact required text is available as reusable asset |
| P2B-DOC-07 | P0 | Export structured scheme metadata deliverable | Data engineer | P1-GOV tasks | Machine-readable file validates against schema |
| P2B-DOC-08 | P0 | Publish versioned evaluation dataset and runner instructions | QA | P1-EVAL, Phase 2B tests | Another engineer can reproduce the report |
| P2B-DOC-09 | P1 | Document known limitations and controlled failure behavior | Product + engineering | Phase 2B | README and user-facing copy are consistent |

### 11.8 MVP Observability

Implement dashboards before declaring feature completeness:

- End-to-end latency and component latency.
- Query classes and refusal reasons.
- Scheme-resolution failures and ambiguity rate.
- Retrieval zero-result rate and correct-evidence evaluation metrics.
- Evidence failures by stale, conflict, source, scope, and date reason.
- Citation and response-contract validation failures.
- Corpus coverage by scheme, fact type, and document type.
- Ingestion freshness and failed source fetches.
- Model token use, timeout rate, and cost per answered request.

### 11.9 Phase Deliverables

- Production-shaped question API and health endpoints.
- Hybrid retrieval and evidence validator.
- Structured extraction and deterministic templates for scalar facts.
- Constrained generation for longer supported facts and procedures.
- Deterministic compliance validator and renderer-owned citations.
- Minimal responsive chat UI with disclaimer and examples.
- README, disclaimer snippet, scheme metadata, and evaluation dataset.
- Quality, coverage, freshness, policy, latency, and cost dashboards.

### 11.10 MVP Exit Gate

Phase 2B is complete when:

- All 35 canonical scheme names and approved aliases resolve correctly in the release dataset.
- Every required factual question type has answerable and insufficient-evidence cases.
- Critical advisory, recommendation, ranking, prediction, and comparison cases have zero false factual answers.
- Factual responses have 100% official-domain and exactly-one-citation compliance.
- Last-updated dates match selected evidence in 100% of release cases.
- Unsupported factual claims are zero in the release-gate dataset.
- Retrieval Recall@5 is at least 95% on answerable factual questions.
- End-to-end exact fact accuracy is at least 95%, with every failure reviewed.
- Response bodies contain no more than three sentences.
- Sensitive-data values do not appear in generated output or standard telemetry.
- Product and domain reviewers sign off on a representative sample for all fact types.
- Required documentation deliverables are complete and reproducible.

## 12. Phase 3A - Quality, Security, and Resilience Hardening

### 12.1 Goal

Turn the feature-complete MVP into a trustworthy release candidate by addressing source change, conflict, adversarial behavior, dependency failure, performance, privacy, and operational recovery.

### 12.2 Workstream A - Corpus Publication and Conflict Operations

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3-COR-01 | P0 | Implement explicit supersedes/superseded-by relationships | Data engineer + domain reviewer | P2B-EVD-08 | Effective chains are queryable and tested |
| P3-COR-02 | P0 | Build conflict records and operator review workflow | Data/backend + domain reviewer | P3-COR-01 | Review decision is audited; unresolved facts stay blocked |
| P3-COR-03 | P0 | Implement staging manifest approval | Data + platform | Phase 2B | Only approved manifests can become active |
| P3-COR-04 | P0 | Implement blue/green index publication | Platform + RAG engineer | P3-COR-03 | Serving alias switches atomically |
| P3-COR-05 | P0 | Implement index and corpus rollback | Platform engineer | P3-COR-04 | Rollback drill completes within target |
| P3-COR-06 | P1 | Add source-link availability checks | Data engineer | P1-GOV-05 | Broken Groww links alert and invoke approved behavior |
| P3-COR-07 | P1 | Add parser anomaly and coverage-regression detection | Data + QA | P3-COR-03 | Missing schemes/facts block publication |
| P3-COR-08 | P1 | Build minimal corpus administration view or CLI | Backend/data | P3-COR-02 through P3-COR-07 | Operator can inspect quarantine, conflicts, and manifests |

### 12.3 Workstream B - Safety and Privacy Hardening

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3-SEC-01 | P0 | Execute prompt-injection tests against source documents | Security + QA | Phase 2B | Retrieved instructions cannot alter policy or invoke tools |
| P3-SEC-02 | P0 | Run mixed-intent and obfuscated-advice adversarial suite | QA + product | Phase 2B | Critical policy gate remains zero false allows |
| P3-SEC-03 | P0 | Verify Groq model endpoints have no browsing or administrative tools | Security + RAG engineer | P0-06 | Runtime configuration evidence recorded |
| P3-SEC-04 | P0 | Complete secrets, IAM, network, and encryption review | Security + platform | Production infrastructure | No unresolved high-severity findings |
| P3-SEC-05 | P0 | Verify telemetry redaction and retention enforcement | Security + platform | P0-07, Phase 2B | Test values are absent or removed on schedule |
| P3-SEC-06 | P1 | Add dependency, container, and secret scanning gates | Platform engineer | CI pipeline | High-severity findings block release |
| P3-SEC-07 | P1 | Complete API abuse, injection, and oversized-input tests | Security + QA | P2B-API-03 | Controls operate at edge and application layers |
| P3-SEC-08 | P0 | Update threat model with implemented controls and residual risks | Security + engineering | P3-SEC-01 through P3-SEC-07 | Formal production review completed |

### 12.4 Workstream C - Reliability and Graceful Degradation

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3-REL-01 | P0 | Add per-component timeouts and transient retry policy | Backend + platform | Phase 2B | Timeout and retry integration tests pass |
| P3-REL-02 | P0 | Add model and embedding service circuit breakers | Backend engineer | P3-REL-01 | Failure drill avoids request pileup |
| P3-REL-03 | P0 | Implement lexical-only degradation with full evidence validation | RAG engineer | P3-REL-01 | Vector outage still answers only validated cases |
| P3-REL-04 | P0 | Verify metadata-store failure always returns unavailable | Backend + QA | P3-REL-01 | Provenance checks cannot be bypassed |
| P3-REL-05 | P1 | Implement evidence-version-aware answer cache | Backend engineer | Phase 2B | Corpus/policy/template changes invalidate cached answers |
| P3-REL-06 | P1 | Apply short and safe caching rules to refusal types | Backend + product | P3-REL-05 | Ambiguity and evidence failures do not remain stale |
| P3-REL-07 | P0 | Run source, index, database, cache, and model failure drills | Platform + QA | P3-REL-01 through P3-REL-06 | Expected terminal states and alerts are observed |
| P3-REL-08 | P0 | Verify previous approved corpus remains active on ingestion failure | Data + platform | P3-COR-04 | Failed ingest cannot replace active corpus |

### 12.5 Workstream D - Performance and Accessibility

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3-PERF-01 | P0 | Create representative load profile and test harness | QA + platform | Phase 2B | Reproducible p50/p95/p99 report |
| P3-PERF-02 | P0 | Tune database, indexes, candidate counts, reranking, and context limits | RAG + backend | P3-PERF-01 | Quality gates preserved while latency meets target |
| P3-PERF-03 | P1 | Tune cache policy and capacity | Backend + platform | P3-REL-05, P3-PERF-01 | Cache improves latency without stale citations |
| P3-PERF-04 | P0 | Validate responsive behavior on supported browsers and devices | Frontend + QA | Phase 2B UI | Browser/device matrix passes |
| P3-PERF-05 | P0 | Complete manual WCAG-oriented accessibility review | Frontend + accessibility reviewer | P2B-UI-08 | No unresolved critical accessibility defects |
| P3-PERF-06 | P1 | Verify cost per answered and refused query | Platform + product | Load test | Cost dashboard and operating estimate approved |

### 12.6 Workstream E - Evaluation Hardening

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3-EVAL-01 | P0 | Expand paraphrases and typo cases using reviewed production-like language | QA + product | Phase 2B | Dataset diversity report is approved |
| P3-EVAL-02 | P0 | Add mutation tests for source, date, number, scheme, plan, and citation changes | QA | Phase 2B | Every mutation is rejected |
| P3-EVAL-03 | P0 | Add historical-versus-current and close-date conflict cases | QA + domain reviewer | P3-COR-01 | Current applicability is selected or conflict returned |
| P3-EVAL-04 | P0 | Add full prompt-injection and privacy benchmark | Security + QA | P3-SEC-01 | Benchmark meets zero-tolerance gates |
| P3-EVAL-05 | P0 | Implement replay comparison across model, prompt, policy, parser, and index versions | QA + RAG engineer | Versioned audit records | Candidate changes produce comparable reports |
| P3-EVAL-06 | P0 | Establish human review sampling rubric | Product + domain reviewer | Phase 2B | Reviewers score fact, evidence, scope, and wording consistently |
| P3-EVAL-07 | P0 | Run release-candidate evaluation and triage every failure | QA + all owners | P3-EVAL-01 through P3-EVAL-06 | Signed release-candidate report |

### 12.7 Phase Deliverables

- Supersession and conflict-management workflow.
- Blue/green corpus publication and tested rollback.
- Security, privacy, prompt-injection, and abuse test reports.
- Graceful-degradation logic and failure-drill report.
- Evidence-version-aware caching.
- Load, latency, cost, browser, and accessibility reports.
- Expanded adversarial evaluation and replay tooling.
- Production release candidate.

### 12.8 Exit Gate

Phase 3A is complete when:

- No unresolved high-severity security, privacy, accessibility, or reliability finding remains.
- Unresolved source conflicts suppress factual answers.
- Corpus publication and rollback have been exercised successfully.
- Every mandatory failure scenario produces its specified user response and operational alert.
- Latency and cost satisfy approved targets without weakening retrieval or evidence gates.
- Production telemetry is redacted and retention controls are active.
- Release-candidate evaluation meets every zero-tolerance policy, citation, date, and unsupported-claim gate.
- Product, domain, QA, security, and engineering owners approve the release candidate.

## 13. Phase 3B - Production Readiness and Rollout

### 13.1 Goal

Deploy the approved release candidate safely, establish operational ownership, and verify real production behavior before broad availability.

### 13.2 Work Packages

| ID | Priority | Task | Primary owner | Dependencies | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| P3B-01 | P0 | Provision isolated production network, compute, data stores, secrets, and telemetry | Platform engineer | Phase 3A | Infrastructure review and smoke tests pass |
| P3B-02 | P0 | Publish approved application, policy, and corpus manifests | Platform + release owner | P3B-01 | Versions visible in health and audit output |
| P3B-03 | P0 | Configure dashboards and paging alerts | Platform + service owner | P3B-01 | Test alerts reach named responders |
| P3B-04 | P0 | Finalize runbooks for source failure, conflict, model outage, index rollback, privacy incident, and high refusal rates | Service owner | Phase 3A | Tabletop exercise completed |
| P3B-05 | P0 | Define support escalation and domain-review rotation | Product + service owner | P3B-04 | Named ownership and response expectations published |
| P3B-06 | P0 | Run production smoke evaluation using non-sensitive synthetic queries | QA + release owner | P3B-02 | Smoke report passes all contract checks |
| P3B-07 | P0 | Enable internal users or controlled allowlist | Product + platform | P3B-06 | Feedback is captured without policy bypass |
| P3B-08 | P0 | Run canary rollout with automated rollback criteria | Release owner | P3B-07 | Canary metrics remain within gates |
| P3B-09 | P0 | Expand rollout in approved stages | Release owner + product | P3B-08 | Each stage has documented go/no-go decision |
| P3B-10 | P0 | Complete post-launch review after initial observation window | All owners | P3B-09 | Findings, incidents, and follow-ups recorded |

### 13.3 Suggested Rollout Stages

| Stage | Audience | Minimum observation | Go criteria |
| --- | --- | --- | --- |
| Internal QA | Delivery team and domain reviewers | One complete corpus refresh cycle | No contract or evidence failures |
| Internal pilot | Selected support/content users | 3-5 business days | Safety gates pass; failure patterns understood |
| Limited production | Small approved traffic percentage | At least 24 hours and representative volume | Error, latency, refusal, and quality metrics within limits |
| Expanded production | Increasing traffic stages | At least one business cycle per stage | No regression and responders remain ready |
| General availability | Approved target audience | Continuous | Production SLOs and quality gates active |

Traffic percentages should be chosen based on actual volume. A fixed percentage is not useful when traffic is too low to produce representative evidence.

### 13.4 Automatic Rollback Conditions

Rollback or disable factual answers when any approved critical threshold is breached, including:

- Any verified unsupported factual claim.
- Any factual response with a prohibited or non-official citation.
- Any advice or recommendation returned from a prohibited query.
- Systematic wrong-scheme or wrong-plan resolution.
- Corpus manifest corruption or incomplete coverage publication.
- Sensitive values appearing in model requests, responses, or standard telemetry.
- Sustained availability or latency breach beyond the approved window.

The system may remain available in refusal-only mode if that mode has been implemented and validated.

### 13.5 Production Exit Gate

The initial production release is complete when:

- General availability is approved by product, domain, engineering, QA, security, and operations owners.
- Dashboards, alerts, runbooks, escalation, and rollback are active.
- The latest approved corpus manifest covers all 35 schemes according to the coverage policy.
- No zero-tolerance gate has failed during rollout.
- Initial user feedback and refusal patterns have named follow-up actions.
- A post-launch review records actual SLOs, costs, incidents, and backlog priorities.

## 14. Phase 4 - Controlled Expansion

### 14.1 Goal

Expand scope only through repeatable onboarding gates. New plans, options, schemes, AMCs, languages, and service boundaries must not inherit unvalidated assumptions from the HDFC Direct Growth MVP.

### 14.2 Expansion Entry Criteria

- Initial production SLOs and quality gates have remained stable for an approved observation period.
- Corpus operations and domain review capacity can support added scope.
- The requested expansion has an owner, source inventory, evaluation budget, and rollback plan.
- Expansion does not weaken zero-tolerance policy and citation rules.

### 14.3 Expansion Tracks

#### Track A - Regular Plans and Non-Growth Options

| ID | Priority | Task | Completion evidence |
| --- | --- | --- | --- |
| P4-PLAN-01 | P1 | Approve supported plan/option matrix | Product and domain approval |
| P4-PLAN-02 | P1 | Extend canonical identifiers and aliases without changing existing IDs | Registry migration and compatibility tests |
| P4-PLAN-03 | P1 | Add plan/option-specific source and extraction fixtures | Domain-reviewed evidence set |
| P4-PLAN-04 | P1 | Expand ambiguity and explicit-plan resolution tests | No silent fallback in evaluation |
| P4-PLAN-05 | P1 | Run full retrieval, answer, citation, and regression gates | Expansion report meets all thresholds |

#### Track B - Additional Schemes or AMCs

| ID | Priority | Task | Completion evidence |
| --- | --- | --- | --- |
| P4-AMC-01 | P1 | Complete source-policy and access review for the new AMC | Approved source registry changes |
| P4-AMC-02 | P1 | Create isolated scheme catalog and parser fixtures | New coverage report |
| P4-AMC-03 | P1 | Validate source precedence and document semantics | Domain-approved fact matrix |
| P4-AMC-04 | P1 | Build balanced evaluation dataset for new scope | Required facts, refusals, conflicts, aliases covered |
| P4-AMC-05 | P1 | Canary new scope independently | Existing HDFC behavior shows no regression |

#### Track C - Additional Languages

| ID | Priority | Task | Completion evidence |
| --- | --- | --- | --- |
| P4-LANG-01 | P2 | Approve language, script, terminology, and source-display rules | Localization specification |
| P4-LANG-02 | P2 | Add language-specific classifier and scheme-resolution evaluation | Metrics meet critical policy gates |
| P4-LANG-03 | P2 | Validate numeric, date, currency, plan, and option rendering | Locale contract tests |
| P4-LANG-04 | P2 | Conduct native-language domain review | Signed evaluation sample |
| P4-LANG-05 | P2 | Roll out by locale with independent monitoring | No cross-locale regression |

#### Track D - Service Decomposition

Split the modular monolith only when measured evidence supports it, such as:

- A component requires materially different scaling.
- Independent ownership or deployment frequency creates delivery contention.
- Failure isolation cannot be achieved inside the current service.
- Model or retrieval latency requires specialized infrastructure.

Any split must preserve the orchestrator's mandatory ordering, typed contracts, trace continuity, and fail-closed behavior.

### 14.4 Expansion Exit Gate

Each expansion is independently complete only when:

- New source and domain rules are approved.
- New entities have canonical IDs and reviewed aliases.
- Required parser, retrieval, policy, answer, citation, and conflict fixtures exist.
- Existing-scope regression gates still pass.
- New-scope zero-tolerance gates pass.
- A reversible rollout and named operational owner exist.

## 15. Cross-Phase Test Plan

### 15.1 Test Pyramid

| Layer | Runs | Gate purpose |
| --- | --- | --- |
| Unit | Every change | Rules, parsing helpers, dates, schemas, templates, sentence/link counts |
| Contract | Every change | API, evidence, model output, renderer, and audit compatibility |
| Parser fixtures | Every ingestion change | Preserve page, table, heading, row, footnote, and date meaning |
| Integration | Every pull request or merge | Stores, indexes, queue, retrieval, model adapters, orchestrator |
| Evaluation subset | Every pull request | Fast classifier, resolver, retrieval, and response regressions |
| Full evaluation | Nightly and before release | All schemes, fact types, policy, conflict, privacy, and injection cases |
| End-to-end UI | Staging and before release | Chat states, disclaimer, one source, footer, accessibility |
| Resilience/load | Before release and material infrastructure changes | Degradation, rollback, SLO, and cost behavior |

### 15.2 Mandatory Test Categories

- Canonical and alias queries for every scheme.
- Expense ratio, exit load, minimum SIP, minimum lump sum, benchmark, riskometer, lock-in, investment objective, fund manager, launch date, plans/options, factsheet location, account statement, capital-gains statement, and permitted single performance value.
- Advice, recommendation, ranking, prediction, comparison, and calculation requests.
- Mixed factual/advisory and obfuscated prohibited requests.
- Unsupported scheme, fact, plan, option, and date requests.
- Missing, stale, superseded, and conflicting evidence.
- Wrong scheme, wrong plan, wrong option, wrong page, and generic-source citations.
- One, two, and more-than-one citation mutations.
- Wrong source date and ingestion-date substitution.
- Three-sentence boundary and fourth-sentence rejection.
- PAN, Aadhaar, bank, OTP, email, phone, login, and transaction data.
- Prompt-injection content inside the user query and retrieved document.
- Model, vector index, keyword index, metadata database, cache, and source-fetch failures.

## 16. Evaluation Dataset Growth Plan

| Milestone | Minimum coverage objective |
| --- | --- |
| End Phase 0 | 30-50 seed questions across facts, refusals, ambiguity, and privacy |
| End Phase 1 | Every required class and fact type; all 35 schemes represented in resolution tests |
| End Phase 2A | Complete gold evidence and end-to-end expectations for the vertical slice |
| End Phase 2B | All fact types, all schemes, answer/refusal balance, stale/conflict/unsupported cases |
| End Phase 3A | Adversarial paraphrases, prompt injection, privacy, mutations, failures, historical conflicts |
| Phase 4 | Independent balanced datasets for every added plan, option, AMC, or language |

Every factual case should include:

- Query and reviewed paraphrases.
- Expected class, fact type, and scope.
- Expected canonical scheme, plan, and option.
- Gold document and passage IDs.
- Expected value or supported summary points.
- Expected citation URL and evidence date.
- Expected response type.
- Difficulty and regression tags.

## 17. CI/CD Implementation Plan

### 17.1 Application Pipeline

1. Validate configuration and contracts.
2. Format, lint, and type-check.
3. Run unit, contract, and fast evaluation tests.
4. Scan dependencies, secrets, and container configuration.
5. Build an immutable application artifact.
6. Run integration tests against pinned services and corpus fixtures.
7. Deploy the same artifact to staging.
8. Run full evaluation, UI, accessibility, and smoke suites.
9. Produce a signed or checksummed release report.
10. Promote through canary stages using versioned configuration.

### 17.2 Corpus Pipeline

1. Discover approved sources.
2. Fetch and hash source versions.
3. Parse, normalize, map, and chunk.
4. Extract metadata and facts.
5. Generate versioned embeddings.
6. Build a staging manifest and indexes.
7. Run domain, source, parser, coverage, and retrieval checks.
8. Quarantine failures and unresolved conflicts.
9. Approve the candidate manifest.
10. Atomically publish the serving alias.
11. Run post-publication smoke and regression checks.
12. Roll back automatically when a critical publication gate fails.

Application and corpus releases remain independent but each response records both version sets.

## 18. Configuration and Feature Flags

Use versioned, reviewable configuration for:

- Approved domains and document types.
- Scheme catalog and aliases.
- Fact-type source precedence.
- Freshness thresholds.
- Classification rules and confidence thresholds.
- Fuzzy scheme-match threshold.
- Retrieval candidate counts, fusion, and reranking.
- Allowed response and refusal types.
- Prompt and deterministic template versions.
- Model endpoints and generation limits.
- Query, trace, and audit retention.
- Feature availability by scheme, fact type, plan, option, and locale.

Required operational flags:

- Disable all factual answers and run refusal-only mode.
- Disable model generation while preserving deterministic scalar answers.
- Disable a fact type with known evidence issues.
- Disable one scheme without affecting the rest of the corpus.
- Pin serving to a previous corpus manifest.
- Disable vector retrieval and use validated lexical degradation.

Feature flags must never enable unapproved sources or bypass evidence/compliance validation.

## 19. Data Migration and Backfill Plan

1. Use forward-only database migrations with tested rollback or compensating procedures.
2. Keep source documents immutable; create new versions rather than updating evidence in place.
3. Version parser, normalizer, chunker, embedding, and extraction outputs.
4. Reprocess into staging when any transformation version changes.
5. Compare candidate coverage and retrieval metrics with the active manifest.
6. Publish only after release gates pass.
7. Retain the previous manifest and indexes for rollback.
8. Record which source and transformation version produced every fact and passage.

Backfills should be restartable and idempotent. Partial backfills cannot replace a complete active corpus.

## 20. Operational Runbooks Required

| Runbook | Owner | Required by |
| --- | --- | --- |
| Groww source unavailable or moved | Data/service owner | Phase 3B |
| Parser output or coverage regression | Data engineer | Phase 3A |
| Conflicting current facts | Domain reviewer + service owner | Phase 3A |
| Stale source beyond threshold | Data/service owner | Phase 3A |
| Model provider outage or degradation | Service owner | Phase 3A |
| Keyword/vector index outage | Service owner | Phase 3A |
| Corpus publication and rollback | Platform + data | Phase 3A |
| Wrong scheme, fact, or citation incident | Product + engineering | Phase 3B |
| Policy breach or advisory answer | Product + security + engineering | Phase 3B |
| Sensitive-data exposure | Security/privacy | Phase 3B |
| Elevated refusal or insufficient-evidence rate | Product + RAG owner | Phase 3B |
| Cost or latency regression | Platform + engineering | Phase 3B |

## 21. Key Risks and Delivery Responses

| Risk | Earliest detection phase | Delivery response |
| --- | --- | --- |
| Source access or usage prevents planned ingestion | Phase 0 | Confirm policies before fetcher implementation; identify compliant official alternatives |
| 35-scheme source coverage is incomplete | Phase 1 | Publish coverage report early; refuse uncovered facts; prioritize missing Groww sources |
| PDFs lose table qualifiers | Phase 1 | Add representative fixtures, layout extraction, and domain visual review |
| Source precedence remains disputed | Phase 0 | Block affected fact types rather than embedding unresolved interpretation in code |
| Classifier mistakes advisory intent for factual | Phase 1 | Conservative merger, critical zero-tolerance suite, fixed refusal on low confidence |
| Retrieval returns a plausible wrong scheme | Phase 2A | Hard scheme filters, stable IDs, alias tests, and ambiguity response |
| Model adds plausible unsupported content | Phase 2A | Prefer templates, bind evidence IDs, validate claims, and allow one repair only |
| Citation and answer evidence diverge | Phase 2A | Renderer uses evidence-validator output, never model-provided URLs |
| Fresh corpus breaks prior answers | Phase 3A | Candidate manifests, replay evaluation, blue/green publication, rollback |
| Production logs contain personal values | Phase 1 and Phase 3A | Pre-model guard, redaction tests, restricted retention, security review |
| Team optimizes answer rate by weakening rules | Every phase | Keep policy/citation/unsupported-claim gates immutable without explicit approval |
| MVP scope expands before quality stabilizes | Phase 2B | Require Phase 3B exit before Phase 4 onboarding |

## 22. Decision and Escalation Rules

Implementation must pause for product/domain/security review when:

- Two current Groww sources disagree and configured precedence does not resolve the fact.
- An Groww document applies to a scheme but plan or option scope is unclear.
- A source lacks a reliable publication or effective date.
- A requested fact would require calculation or interpretation.
- A new source domain, document type, or data region is proposed. Groq is the initial model provider for the MVP.
- A change could expose user input beyond approved retention or processing boundaries.
- A release candidate violates a zero-tolerance gate.

The team may continue unrelated work while the affected fact, source, or feature remains disabled.

## 23. Deliverable Traceability

| Required deliverable or outcome | Planned implementation | Completion phase |
| --- | --- | --- |
| README | P2B-DOC-01 through P2B-DOC-05, P2B-DOC-09 | Phase 2B |
| Disclaimer snippet | P2B-DOC-06 and P2B-UI-03 | Phase 2B |
| Metadata for all 35 schemes | P1-GOV-01 through P1-GOV-09, P2B-DOC-07 | Phase 2B |
| Evaluation dataset | P0-15, P1-EVAL tasks, P2A-15, P3-EVAL tasks | Continuous; release-ready Phase 3A |
| Approved-source retrieval | P1-GOV-05, P1-ING tasks, P2A-01 through P2A-05 | Phase 2A |
| Scheme alias resolution | P1-GOV-04 and P1-RES tasks | Phase 1 |
| Latest-applicable evidence | P1-GOV-06/07, P2B-EVD-08/09, P3-COR tasks | Phase 3A |
| Advice and comparison refusal | P1-POL tasks and P3-SEC-02 | Phase 1; hardened Phase 3A |
| Exactly one official citation | P2A-09/10 and P2B-ANS-07/09 | Phase 2A |
| Three-sentence maximum | P2A-09 and P2B-ANS-07 | Phase 2A |
| Evidence-derived last-updated footer | P2A-05/10 | Phase 2A |
| Visible chat disclaimer and examples | P2B-UI-02/03 | Phase 2B |
| No sensitive-data processing | P1-POL-06, P2B-UI-06, P3-SEC-05 | Phase 3A |
| Fast, observable service | P2B observability, P3-PERF tasks | Phase 3A |
| Safe corpus refresh and rollback | P3-COR tasks | Phase 3A |

## 24. Milestone Review Checklist

At every phase review, record:

- Completed and deferred task IDs.
- Demonstrated deliverables.
- Evaluation manifest, corpus manifest, policy version, and application version.
- Current quality, latency, cost, freshness, and coverage metrics.
- Open defects and risk severity.
- Decisions made or escalated.
- Scope changes and their effect on later phases.
- Explicit go, conditional go, or no-go decision with named approvers.

## 25. Immediate Next Actions

The first execution sprint should begin with this sequence:

1. Assign owners for P0-01 through P0-08 and set decision deadlines.
2. Approve source precedence, freshness, mixed-intent, refusal-link, and plan/option behavior.
3. Scaffold the repository, local environment, CI, and shared contracts.
4. Create the 35-scheme registry schema and seed evaluation schema in parallel.
5. Collect one representative source fixture for each Groww document type.
6. Demonstrate a repeatable test report before starting broad ingestion.

No answer-generation prompt should be treated as production work until evidence, policy, and evaluation contracts from Phase 0 and Phase 1 are in place.

## 26. Plan Completion Criteria

This implementation plan is fully executed when:

- The initial 35-scheme assistant is generally available to its approved audience.
- All Phase 3B production exit criteria are met.
- Required documentation and structured deliverables are published.
- Every production answer is traceable to one validated Groww source and source date.
- Zero-tolerance financial-policy, unsupported-claim, citation, and privacy gates are active in CI and production monitoring.
- Corpus refresh, conflict review, incident response, and rollback have named operational owners.
- Phase 4 requests use the controlled onboarding process rather than bypassing the initial architecture.

The execution rule is simple: when evidence, policy, and response validation agree, answer concisely; otherwise, refuse safely and leave an auditable reason.
