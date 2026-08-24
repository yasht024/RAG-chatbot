import pytest
from fastapi.testclient import TestClient
from services.assistant_api.main import app
from services.assistant_api.middleware import RATE_LIMIT_STORE

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rate_limits():
    RATE_LIMIT_STORE.clear()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "3.0.0-rc1"


def test_factual_answer_minimum_sip():
    response = client.post("/v1/questions", json={
        "query": "What is the minimum sip amount for HDFC Mid Cap?",
        "conversation_id": "test_123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FACTUAL_ANSWER"
    assert "minimum SIP amount is ₹100" in data["answer"]
    assert "groww.in" in data["citation"]["url"]
    assert "error" not in data

def test_policy_refusal_recommendation():
    response = client.post("/v1/questions", json={
        "query": "Can you recommend the best HDFC fund?",
        "conversation_id": "test_124"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "POLICY_REFUSAL"
    assert data["answer"] is None
    assert "cannot offer investment advice" in data["error"]["reason"]

def test_insufficient_evidence_unsupported():
    response = client.post("/v1/questions", json={
        "query": "What is the NAV today for HDFC Mid Cap?",
        "conversation_id": "test_125"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "INSUFFICIENT_EVIDENCE"

def test_amc_level_process_query():
    response = client.post("/v1/questions", json={
        "query": "How do I update my KYC?",
        "conversation_id": "test_126"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FACTUAL_ANSWER"
    assert "update your KYC" in data["answer"]

def test_diagnostics_endpoint():
    response = client.get("/v1/internal/retrieval-diagnostics?query=kyc&fact_type=kyc_procedure&amc_level=true")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "AMC_PROCEDURE" in data["document_routing"]
    assert len(data["ranked_passages"]) > 0

def test_source_conflict_resolved():
    response = client.post("/v1/questions", json={
        "query": "What is the exit load for HDFC Mid Cap?",
        "conversation_id": "test_127"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FACTUAL_ANSWER"
    # Groww (1.5%) should win over HDFC AMC (1.0%) due to precedence rules
    assert "1.5%" in data["answer"]

def test_source_conflict_unresolved():
    response = client.post("/v1/questions", json={
        "query": "Who is the fund manager for HDFC Mid Cap?",
        "conversation_id": "test_128"
    })
    assert response.status_code == 200
    data = response.json()
    # Two Groww sources with equal precedence (Gopal vs Rahul) should fail closed
    assert data["status"] == "SOURCE_CONFLICT"

def test_descriptive_generation_and_footer():
    response = client.post("/v1/questions", json={
        "query": "What is the investment objective for HDFC Mid Cap?",
        "conversation_id": "test_129"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FACTUAL_ANSWER"
    assert "long-term capital appreciation" in data["answer"]
    assert "(As of 2026-08-23)" in data["answer"]

def test_semantic_repair_success():
    from services.assistant_api.generator import llm
    from services.assistant_api.main import orchestrator
    orchestrator.answer_cache.invalidate_all()
    # Force it to fail on the 1st attempt, but succeed on the 2nd
    llm.set_test_mode(fail_first_try=True)
    
    response = client.post("/v1/questions", json={
        "query": "What is the investment objective for HDFC Mid Cap?",
        "conversation_id": "test_130"
    })
    
    assert response.status_code == 200
    data = response.json()
    # It should have repaired itself
    assert data["status"] == "FACTUAL_ANSWER"
    assert "guarantees" not in data["answer"]
    assert "long-term capital appreciation" in data["answer"]
    assert llm.attempt == 2  # It took 2 attempts

def test_semantic_repair_fail_closed():
    from services.assistant_api.generator import llm
    from services.assistant_api.main import orchestrator
    orchestrator.answer_cache.invalidate_all()
    # Force it to fail always
    llm.set_test_mode(fail_always=True)
    
    response = client.post("/v1/questions", json={
        "query": "What is the investment objective for HDFC Mid Cap?",
        "conversation_id": "test_131"
    })
    
    assert response.status_code == 200
    data = response.json()
    # It should fail closed since both attempts hallucinated
    assert data["status"] == "INSUFFICIENT_EVIDENCE"
    assert data["answer"] is None
    
    # Reset LLM
    llm.set_test_mode(fail_first_try=False, fail_always=False)
    orchestrator.answer_cache.invalidate_all()


def test_pii_redaction():
    # Provide a mock PAN and phone number in the query
    response = client.post("/v1/questions", json={
        "query": "My PAN is ABCDE1234F and phone is 9876543210. What is the exit load for HDFC Mid Cap?",
        "conversation_id": "test_132"
    })
    
    assert response.status_code == 200
    
    # We can check internal orchestrator logs or verify the answer is still returned cleanly
    # In a real system, we'd mock the orchestrator to verify the redacted string.
    # Here we just verify the system handled it without crashing and returned the answer.
    data = response.json()
    assert data["status"] == "FACTUAL_ANSWER"

def test_idempotency():
    payload = {
        "query": "What is the exit load for HDFC Mid Cap?",
        "conversation_id": "test_133"
    }
    # Request 1
    resp1 = client.post("/v1/questions", json=payload, headers={"Idempotency-Key": "idem_123"})
    assert resp1.status_code == 200
    
    # Request 2 (should be cached)
    resp2 = client.post("/v1/questions", json=payload, headers={"Idempotency-Key": "idem_123"})
    assert resp2.status_code == 200
    
    assert resp1.json() == resp2.json()

def test_rate_limiting():
    # Hit the API 15 times to trigger the 10 req / 60s limit
    # We use a unique endpoint like health check or questions
    payload = {
        "query": "What is the exit load for HDFC Mid Cap?",
        "conversation_id": "test_134"
    }
    
    for _ in range(10):
        client.post("/v1/questions", json=payload)
        
    # The 11th request should be rate limited
    resp_11 = client.post("/v1/questions", json=payload)
    assert resp_11.status_code == 429
    assert resp_11.json()["detail"] == "Too Many Requests"
