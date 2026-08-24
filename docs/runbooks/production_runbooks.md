# Production Operations Runbooks (Phase 3B - P3B-04)

This document contains standard operating procedures (SOPs) for responding to operational, data, security, and model incidents.

---

## 1. Runbook: Source Failure / Broken Groww Links (`P3-COR-06`)
* **Trigger:** Alert `GROWW_SOURCE_UNAVAILABLE` or `CORPUS_QUALITY_CHECK_FAILED`.
* **Impact:** Ingestion pipeline cannot fetch latest factsheets/metadata.
* **Procedure:**
  1. Inspect `/v1/internal/manifests` to ensure currently serving active corpus manifest is locked.
  2. Run `python -m packages.corpus.cli manifests` to verify the active Blue/Green slot.
  3. Validate if Groww URL scheme changed; if so, update canonical mappings in `data/catalog/aliases.json`.
  4. Block new manifest publication until `CorpusQualityChecker.validate_source_links` returns 100% valid.

---

## 2. Runbook: Conflicting Source Facts & Quarantine Triage (`P3-COR-02`)
* **Trigger:** Alert `SOURCE_CONFLICT_QUARANTINED` or API returns `TerminalState.SOURCE_CONFLICT`.
* **Impact:** Queries targeting the conflicted scheme/fact are safely failing closed.
* **Procedure:**
  1. Call `GET /v1/internal/conflicts` or run `python -m packages.corpus.cli list-conflicts` to view the competing source passages.
  2. Cross-reference with the latest official AMC regulatory notice or SEBI filing.
  3. Resolve the conflict via `POST /v1/internal/conflicts/resolve` specifying the verified winning passage ID, operator identity, and reason.
  4. Once resolved, the fact is automatically unquarantined and answers are resumed.

---

## 3. Runbook: LLM Provider Outage or Rate Limit Quota Depletion (`P3-REL-02`, `P3-REL-05`)
* **Trigger:** Circuit breaker `llm_generation_service` transitions to `OPEN` or `RateLimitExceeded` logged.
* **Impact:** External LLM calls are blocked.
* **Procedure:**
  1. Verify `/health` endpoint to inspect `vector_breaker_state` and `llm_limits`.
  2. System automatically degrades to local deterministic extraction templates (`generate_scalar_answer` and deterministic local summaries).
  3. Ensure `EvidenceAwareAnswerCache` is warm to minimize upstream API calls.
  4. If outage is permanent, switch `GROQ_MODEL` or provider credentials in `.env` without restarting state.

---

## 4. Runbook: Blue/Green Corpus Rollback Drill (`P3-COR-05`, `P3B-08`)
* **Trigger:** Regressions detected post-release or alert `CORPUS_DATA_CORRUPTION`.
* **Impact:** Serving index contains inaccurate or stale data.
* **Procedure:**
  1. Trigger immediate rollback via `python -m packages.corpus.cli rollback` or `CorpusManifestManager.rollback()`.
  2. The serving slot immediately flips back (e.g. `green` → `blue`).
  3. Answer cache is flushed (`orchestrator.answer_cache.invalidate_all()`).
  4. Verify `/health` shows the previous manifest version active.

---

## 5. Runbook: Security & Sensitive Data / PII Incident (`P3-SEC-05`, Section 13.4)
* **Trigger:** Sensitive financial information detected in logs or model prompts.
* **Impact:** Potential compliance violation.
* **Procedure:**
  1. Trigger emergency lockdown via `RolloutStageManager.trigger_emergency_rollback()`.
  2. System instantly transitions to emergency refusal-only mode (403/Policy Refusal).
  3. Inspect logs and sanitize affected telemetry records.
  4. Verify regex patterns in `packages/policy/privacy_guard.py` cover the novel PII pattern.
  5. Deploy patch and call `RolloutStageManager.reset_emergency_mode()`.

---

## 6. Runbook: Elevated Refusal Rates (`P3B-04`)
* **Trigger:** Refusal rate exceeds 15% of valid query traffic.
* **Impact:** Poor user experience or missing coverage.
* **Procedure:**
  1. Inspect `GET /v1/internal/retrieval-diagnostics` for sample failing queries.
  2. Check if questions involve missing aliases (update `data/catalog/aliases.json`).
  3. Check if questions involve regular plans or non-growth options (verify unsupported message is rendered).
