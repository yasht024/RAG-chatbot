# Mutual Fund FAQ Assistant - Observability & Telemetry Standard

## 1. Request Correlation & Context Propagation

All incoming requests to the API gateway must receive or propagate a unique request trace ID.

* **Header:** `X-Request-ID` (UUID v4)
* **Context Scope:** The request ID must be injected into all Python `logging` contexts, OpenTelemetry spans, database queries, and async task execution payloads.

## 2. Standardized Metric Naming Conventions

All application metrics must follow OpenTelemetry naming conventions using the prefix `mf_assistant.`:

### 2.1 Latency Metrics (Histograms)
* `mf_assistant.request.duration_ms`: Total end-to-end HTTP request processing time.
* `mf_assistant.retrieval.duration_ms`: Hybrid search execution time (vector + keyword + rerank).
* `mf_assistant.llm.duration_ms`: Model generation call latency.

### 2.2 Outcome Counters
* `mf_assistant.query.classification_total`: Count of queries by class (`FACTUAL`, `ADVISORY`, `PERFORMANCE_COMPARISON`, `UNSUPPORTED`).
* `mf_assistant.terminal_state.total`: Count of responses by terminal status (`FACTUAL_ANSWER`, `POLICY_REFUSAL`, `INSUFFICIENT_EVIDENCE`, `AMBIGUOUS_SCHEME`, etc.).
* `mf_assistant.compliance.failures_total`: Count of generator output validation failures by rule ID (`EXCEEDED_SENTENCE_LIMIT`, `MISSING_CITATION`, `DATE_MISMATCH`).

## 3. Log Redaction & Privacy Controls

* **Zero PII Logging:** User query strings must pass through the `Sensitive-Data Guard` before being written to operational logs.
* **Structured JSON Logging:** Production logs must be emitted as single-line JSON.

Example Production Log Entry:
```json
{
  "timestamp": "2026-08-23T22:54:00Z",
  "level": "INFO",
  "request_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
  "event": "query_processed",
  "query_class": "FACTUAL",
  "canonical_scheme": "hdfc_mid_cap",
  "terminal_status": "FACTUAL_ANSWER",
  "latency_ms": 420
}
```
