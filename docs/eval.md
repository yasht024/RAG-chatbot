# Mutual Fund FAQ Assistant - Evaluation Strategy

## 1. Overview
The evaluation strategy for the Mutual Fund FAQ Assistant follows an evidence-first, deterministic approach. Corpus governance, policy rules, and evaluation fixtures are built before broad answer generation. This ensures that RAG quality is measured against stable source material and strict safety contracts.

## 2. Evaluation Dataset Growth Plan

The evaluation dataset will grow progressively with each phase of implementation:

| Milestone | Minimum coverage objective |
| --- | --- |
| End Phase 0 | 30-50 seed questions across facts, refusals, ambiguity, and privacy |
| End Phase 1 | Every required class and fact type; all 35 schemes represented in resolution tests |
| End Phase 2A | Complete gold evidence and end-to-end expectations for the vertical slice |
| End Phase 2B | All fact types, all schemes, answer/refusal balance, stale/conflict/unsupported cases |
| End Phase 3A | Adversarial paraphrases, prompt injection, privacy, mutations, failures, historical conflicts |
| Phase 4 | Independent balanced datasets for every added plan, option, AMC, or language |

## 3. Factual Case Schema

Every factual test case in the evaluation dataset must include:

- Query and reviewed paraphrases.
- Expected class, fact type, and scope.
- Expected canonical scheme, plan, and option.
- Gold document and passage IDs.
- Expected value or supported summary points.
- Expected citation URL and evidence date.
- Expected response type.
- Difficulty and regression tags.

## 4. Test Pyramid

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

## 5. Mandatory Test Categories

The comprehensive evaluation must cover:
- Canonical and alias queries for every scheme.
- All defined factual queries (expense ratio, exit load, minimum SIP, etc.) and permitted single performance values.
- Advice, recommendation, ranking, prediction, comparison, and calculation requests (which must be refused).
- Mixed factual/advisory and obfuscated prohibited requests.
- Unsupported scheme, fact, plan, option, and date requests.
- Missing, stale, superseded, and conflicting evidence.
- Wrong scheme, wrong plan, wrong option, wrong page, and generic-source citations.
- Formatting and mutation tests (one/two/more-than-one citation mutations, wrong source date, fourth-sentence rejection).
- PII and sensitive data tests (PAN, Aadhaar, bank, OTP, email, phone, login, transaction data).
- Adversarial tests (prompt-injection content inside the user query and retrieved document).
- Infrastructure failure drills (Model, vector index, keyword index, metadata database, cache, and source-fetch failures).

## 6. Phase-Specific Evaluation Activities

### Phase 1: Foundation
- **Evaluators**: Build classifier and resolver evaluation runners.
- **Fixtures**: Create parser quality fixtures (HTML/PDF/table) and visually review.
- **Negative Cases**: Add stale, conflicting, wrong-plan, wrong-option, and unsupported evidence cases.
- **Adversarial**: Add initial prompt-injection and sensitive-data cases.

### Phase 2: MVP and Slice
- **End-to-End**: Build evaluation for the vertical slice ensuring answer, source, date, and refusal assertions pass.
- **Retrieval**: Complete retrieval evaluation and error analysis (Recall@5 and correct-document metrics).
- **Semantics**: Implement semantic claim-to-evidence validation rejecting unsupported additions.
- **API**: Add API integration test suite with pinned corpus asserting all terminal response types.

### Phase 3: Hardening
- **Diversity**: Expand paraphrases and typo cases using reviewed production-like language.
- **Mutations**: Add mutation tests for source, date, number, scheme, plan, and citation changes to ensure they are rejected.
- **Conflicts**: Add historical-versus-current and close-date conflict cases.
- **Replay**: Implement replay comparison across model, prompt, policy, parser, and index versions using versioned audit records.
- **Human Review**: Establish human review sampling rubric (scoring fact, evidence, scope, and wording).
- **Release Gate**: Run release-candidate evaluation and triage every failure.

## 7. Exit Gates
Before any production rollout (Phase 3B):
- No zero-tolerance policy, citation, date, and unsupported-claim gate can fail.
- Retrieval Recall@5 must be at least 95% on answerable factual questions.
- End-to-end exact fact accuracy must be at least 95%, with every failure reviewed.
- Smoke evaluation using non-sensitive synthetic queries must pass all contract checks in the production environment.
