# HDFC Mutual Fund FAQ RAG Agent — Improvement Plan

## Background

The existing system is a Python-based RAG pipeline that answers factual questions about HDFC Mutual Fund schemes. After thorough inspection, multiple critical failures have been identified. This plan proposes **targeted, surgical fixes** in phase order without rebuilding working components.

---

## Critical Failures Found

### F1 — Groww in `sources.json` and `AMC_PROCEDURE_PASSAGES`
[sources.json](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/data/catalog/sources.json) still lists `groww.in` as an **allowed domain**. The KYC passage in [`search.py`](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/retrieval/search.py#L25) has `source_url: "https://groww.in/mutual-funds/default"`. `validation.py` has `SOURCE_PRECEDENCE = {"groww.in": 100, "hdfcfund.com": 50}` — Groww is rated **higher priority than HDFC AMC**.

### F2 — compliance.py allows Groww in citation check
[compliance.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/compliance.py#L21) checks `"groww.in" or "hdfcfund.com"` as valid citation domains — Groww passes the final compliance gate.

### F3 — Date bug: `publication_date = TODAY_STR`
[corpus_loader.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/retrieval/corpus_loader.py#L184) stamps every passage with today's date. This causes the "As of 2026-08-30" fabrication. No actual source date is preserved.

### F4 — Processed JSONs are sourced from Groww
Every file in `data/processed/` has `canonical_url: "https://groww.in/..."` and `document_title: "... | Groww"`. The corpus_loader overrides the citation URL to HDFC AMC but the underlying **fact values were scraped from Groww** with no official source date.

### F5 — No multi-part query decomposition
The orchestrator picks a single `fact_type` from the query. Multi-part questions like "investment objective, benchmark, fund manager, riskometer, minimum SIP, min lumpsum, exit load, expense ratio" result in only the first detected fact type being answered.

### F6 — Fact-type detection: keyword ladder only
[orchestrator.py lines 105–149](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/orchestrator.py#L105-L149) uses a sequential if-elif chain. First keyword match wins. Multi-field queries are silently truncated.

### F7 — `performance_value` not handled correctly
When `fact_type == "performance_value"` the generator wraps the passage text as-is. The passage text in the corpus is the Groww page title — not an actual performance figure.

### F8 — `resolver.py` not used by `orchestrator.py`
[SchemeResolver](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/resolver.py) has sophisticated alias, fuzzy, and plan/option parsing — but the orchestrator uses its own simple `_resolve_scheme()` loop directly from `aliases.json`. The full resolver capabilities (plan/option extraction, ambiguity detection) are bypassed.

### F9 — No source-organisation metadata on passages
Passages have `source_url` but no `source_org`, `approved_source`, or `source_type` fields. The filter in `validation.py` operates on URLs only — brittle.

### F10 — No Evidence Object before generation
The orchestrator passes a raw string `passage_text` to the generator. No structured evidence object with `scheme_id`, `fact_type`, `source_org`, `approved`, `confidence` fields exists.

### F11 — `evaluation/runner.py` only tests classifier/resolver, not end-to-end answers
The eval runner does not invoke the orchestrator or check answer content against the 16-question test suite required by the spec.

---

## Proposed Changes (Phase-Wise)

---

### PHASE 1 — Source & Compliance Fixes (Critical Blockers)

> **Goal:** Remove Groww from all approved-source lists, fix the compliance gate, fix SOURCE_PRECEDENCE.

#### [MODIFY] [sources.json](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/data/catalog/sources.json)
- Remove `groww.in` from `allowed_domains` and `allowed_url_prefixes`.
- Add `hdfcfund.com`, `amfiindia.com`, `sebi.gov.in` as allowed.
- Add `groww.in` to `prohibited_domains`.

#### [MODIFY] [compliance.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/compliance.py)
- Remove `groww.in` from the valid citation domain check.
- Accept only: `hdfcfund.com`, `amfiindia.com`, `sebi.gov.in`.
- Fix the `(As of <date>)` footer — rename to `Last updated from sources: <date>`.

#### [MODIFY] [validation.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/validation.py)
- Invert SOURCE_PRECEDENCE: `hdfcfund.com = 100`, `amfiindia.com = 90`, `sebi.gov.in = 80`, `groww.in = -1` (rejected).
- Add a hard pre-filter: reject any candidate whose `source_url` contains a prohibited domain before any other logic runs.
- Expand `get_domain()` to cover all approved/prohibited domains.

#### [MODIFY] [search.py AMC_PROCEDURE_PASSAGES](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/retrieval/search.py#L13-L66)
- Replace `source_url: "https://groww.in/mutual-funds/default"` in KYC passage with `"https://www.hdfcfund.com/investor-desk/kyc"`.
- Replace `publication_date: TODAY_STR` with a real reference date (e.g. `"2025-01-01"` as a conservative known-good date, pending actual sourcing).
- Add `source_org = "HDFC AMC"` and `approved_source = True` to all AMC procedural passages.

---

### PHASE 2 — Metadata & Data Layer Fixes

> **Goal:** Add structured metadata to every passage. Fix the date fabrication bug. Enrich processed JSONs.

#### [MODIFY] [corpus_loader.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/retrieval/corpus_loader.py)
- Each passage must carry:
  ```
  source_org, source_domain, source_type, approved_source,
  publication_date (from JSON if available, NOT TODAY_STR),
  effective_date, document_name
  ```
- Stop using `TODAY_STR` as a default `publication_date`. Use `None` or `"unknown"` when unavailable — the renderer must handle that gracefully.
- Add `source_org = "HDFC AMC"` and `approved_source = True` to all loaded passages.

#### [MODIFY] All `data/processed/*.json` files
- Add a `source_org` field: `"HDFC AMC"` for HDFC schemes.
- Add a `source_domain` field: `"hdfcfund.com"`.
- Add a `source_type` field: `"scheme_page"` (as they are product pages, not yet official SIDs/KIMs).
- Add a `publication_date` field with actual date (or `null` if unknown).
- The `canonical_url` will be remapped to official HDFC AMC URL in corpus_loader (already done for citation_url).
- Add `investment_objective` as a fact type where the full_text contains it.

> [!IMPORTANT]
> The data in `data/processed/` was sourced from Groww. The **values** themselves (expense ratio 0.85%, SIP ₹100, etc.) may be accurate, but they have no official source date. Until official HDFC AMC SIDs/KIMs/factsheets are ingested, responses must cite the official HDFC AMC scheme page URL (already done) and use `publication_date: null → "Unknown"` rather than today's date.

---

### PHASE 3 — Scheme Resolver Integration

> **Goal:** Replace the orchestrator's simple alias lookup with the full `SchemeResolver`, gaining plan/option extraction and proper ambiguity handling.

#### [MODIFY] [orchestrator.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/orchestrator.py)
- Replace `_resolve_scheme()` with `SchemeResolver.resolve_scheme()`.
- Pass `plan` and `option` to search calls.
- Handle `UNSUPPORTED_PLAN`, `AMBIGUOUS_SCHEME`, and `UNRESOLVED_SCHEME` responses from the resolver.

---

### PHASE 4 — Fact-Type Extraction & Multi-Part Decomposition

> **Goal:** Extract ALL fact types from a query (not just the first keyword match). Decompose multi-part queries.

#### [NEW] `services/assistant_api/query_decomposer.py`
- Parse a query and return a list of `(fact_type, is_requested)` tuples for all fact types detected.
- Reuse patterns from `QueryClassifier.fact_patterns` and `orchestrator.py`'s keyword ladder, but collect **all** matches instead of the first one.
- For single-fact queries: returns a list of one.
- For multi-field queries: returns all detected facts.

#### [MODIFY] [orchestrator.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/orchestrator.py)
- After scheme resolution, call `QueryDecomposer.decompose(query)` to get the list of requested fact types.
- For each fact type, run a separate retrieval + validation cycle → build a per-fact Evidence Object.
- Collect all evidence objects into a `MultiEvidenceContext`.
- Track `requested_facts` vs `validated_facts`.
- Pass the `MultiEvidenceContext` to the generator.

---

### PHASE 5 — Evidence Object & Source-Validated Context

> **Goal:** Create a structured Evidence Object before generation. The LLM never sees unapproved facts.

#### [NEW] `packages/contracts/evidence.py`
```python
class EvidenceItem(BaseModel):
    scheme_id: str
    fact_type: str
    value: str
    source_org: str
    source_type: str
    source_url: str
    document_name: str
    publication_date: Optional[str]
    effective_date: Optional[str]
    page: Optional[int]
    approved: bool
    confidence: str  # "verified" | "unverified"
```

#### [MODIFY] [orchestrator.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/orchestrator.py)
- Before calling generator, build `List[EvidenceItem]` from validated candidates.
- Pass evidence list to generator, not raw passage text.

---

### PHASE 6 — Generator & Answer Builder for Multi-Part

> **Goal:** Generate answers from Evidence Objects; handle completeness; handle unavailable facts correctly.

#### [MODIFY] [generator.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/generator.py)
- Add `generate_multi_fact_answer(evidence_items: List[EvidenceItem], requested_facts: List[str]) -> str`.
- For each requested fact: if evidence exists → render value; if not → `"Insufficient official evidence found."`.
- Update `generate_scalar_answer` to accept `EvidenceItem` instead of raw passage string.

---

### PHASE 7 — Performance Question Handling

> **Goal:** Allow single factual performance values from approved factsheets; refuse comparisons.

#### [MODIFY] [classifier.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/classifier.py)
- Distinguish `PERFORMANCE_SINGLE` (allowed) from `PERFORMANCE_COMPARISON` (refused).
- `PERFORMANCE_SINGLE`: "What is the 1-year return of HDFC Mid Cap Fund according to its latest official factsheet?" — one scheme, one period, factsheet-attributed.
- `PERFORMANCE_COMPARISON`: Any query comparing two or more schemes OR asking which is better/best.

#### [MODIFY] [orchestrator.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/orchestrator.py)
- For `PERFORMANCE_SINGLE`: retrieve `performance_value` passage, validate, extract figure.
- Since no actual factsheet performance data is in the corpus currently → return `INSUFFICIENT_EVIDENCE` (honest).

---

### PHASE 8 — Final Compliance Validator (Post-Generation)

> **Goal:** Harden the post-generation compliance check. Validate every factual claim. Block prohibited source citations.

#### [MODIFY] [compliance.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/policy/compliance.py)
Add multi-check `enforce_compliance()` that verifies:
1. **Source validation**: citation URL must be approved domain.
2. **Evidence validation**: every factual sentence must map to a validated evidence item.
3. **Scheme validation**: facts belong to the requested scheme.
4. **Date validation**: `last_updated` is from source, not today's date.
5. **Advice validation**: no buy/sell/hold language in answer.
6. **Performance validation**: no comparison/ranking language in answer.
7. **Completeness validation**: all requested fields present (or explicitly marked insufficient).
8. **Citation validation**: exactly one official source URL.

On any failure → `POLICY_REFUSAL` with specific reason.

---

### PHASE 9 — Evaluation Suite & Scorecard

> **Goal:** Create the 16-question evaluation dataset and end-to-end runner.

#### [MODIFY] [data/fixtures/seed_eval.json](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/data/fixtures/seed_eval.json)
- Add all 16 test cases from the spec (factual, performance, advisory, multi-field, out-of-scope).

#### [MODIFY] [evaluation/runner.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/packages/evaluation/runner.py)
- Wire end-to-end: call `Orchestrator.process_query()` for each test case.
- Check: `scheme_detected`, `fact_type_detected`, `source_used`, `source_approved`, `document_date`, `answer`, `citation`, `passed`, `failure_reason`.

#### [NEW] `packages/evaluation/scorecard.py`
- Produce the 10-dimension scorecard from the spec.
- Target thresholds: factual accuracy ≥ 95%, approved-source compliance = 100%, advisory refusal = 100%.

---

### PHASE 10 — System Prompt Refinement

> **Goal:** Update system prompt to precisely match new evidence object format and multi-fact response format.

#### [MODIFY] [system_prompt.py](file:///c:/Users/yash.tiwari/OneDrive/Desktop/Milestone%20-%20RAG/services/assistant_api/system_prompt.py)
- Update response format section to match the spec exactly.
- Explicitly state the `Last updated from sources:` footer rule.
- Explicitly state multi-field answer format.

---

## Files NOT Changed (Working Behaviors to Preserve)

| File | Reason |
|---|---|
| `packages/resilience/` | Circuit breaker, retry, rate limiter work correctly |
| `packages/cache/answer_cache.py` | Cache logic is correct |
| `packages/policy/privacy_guard.py` | PAN/sensitive data guard works |
| `packages/policy/injection_guard.py` | Injection guard works |
| `services/assistant_api/middleware.py` | Request middleware is fine |
| `services/assistant_api/main.py` | FastAPI app structure is fine |
| `packages/corpus/lineage.py` | Supersession logic is correct |
| `packages/corpus/conflicts.py` | Conflict registry is correct |
| `packages/retrieval/fusion.py` | RRF fusion is correct |

---

## Open Questions

> [!IMPORTANT]
> **Data quality**: All 38 processed JSON files were sourced from Groww (evident from `canonical_url` fields). The fact values (SIP amounts, expense ratios, etc.) are product-page scrapes, not from official SIDs/KIMs/factsheets. Until official documents are ingested, the system will always cite `hdfcfund.com` scheme pages (already correct) but the **source dates will be unknown** — the system will output `"Unknown"` for `Last updated from sources` rather than fabricating today's date. Should the team ingest actual SIDs/KIMs, or is the current product-page data acceptable for this milestone?

> [!IMPORTANT]
> **Performance figures**: No performance/return data exists in any processed JSON. For test question 9 ("What is the 1-year return according to the latest official factsheet?"), the system will correctly return `INSUFFICIENT_EVIDENCE`. Is this the expected acceptable outcome for this milestone?

> [!NOTE]
> **Investment objective missing as extracted fact**: The `investment_objective` fact type does not appear in `extracted_facts` arrays in the processed JSONs — only in `full_text`. Phase 2 will add it as a derived passage from `full_text`.

---

## Verification Plan

### Automated Tests
```
python -m pytest tests/ -v
python -m packages.evaluation.runner
```

### Manual Verification
Run all 16 test questions through the API and verify:
- Groww never appears in `citation.url`
- `citation.last_updated` is never today's date
- Multi-part question 14 returns all 8 fields (or marks unavailable)
- Advisory questions 11-13 return `POLICY_REFUSAL`
- Performance comparison question 10 returns `POLICY_REFUSAL`
- Performance single question 9 returns `INSUFFICIENT_EVIDENCE` (no factsheet data in corpus)
