from fastapi.testclient import TestClient
from services.assistant_api.main import app, rollout_manager
from packages.rollout.stage_manager import RolloutStage

client = TestClient(app)


def test_phase3b_production_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["version"] == "3.0.0-rc1"
    assert data["policy_version"] == "2026-08-23.1"
    assert data["corpus"]["version"] == "2.0.0"
    assert data["corpus"]["is_connected"] is True

    # Verify resilience status is reported
    assert data["resilience"]["vector_breaker_state"] in ["CLOSED", "OPEN", "HALF_OPEN"]
    assert "cache_hits" in data["resilience"]

    # Verify user-specified LLM limits are active
    assert data["llm_limits"]["max_rpm"] == 30
    assert data["llm_limits"]["max_rpd"] == 1000
    assert data["llm_limits"]["max_tpm"] == 8000
    assert data["llm_limits"]["max_tpd"] == 200000


def test_phase3b_smoke_queries_factual_and_refusal():
    # Smoke Test 1: Minimum SIP
    r1 = client.post(
        "/v1/questions",
        json={
            "query": "What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
            "conversation_id": "smoke-1",
        },
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "FACTUAL_ANSWER"
    assert "₹100" in r1.json()["answer"]

    # Smoke Test 2: Expense ratio
    r2 = client.post(
        "/v1/questions",
        json={
            "query": "What is the expense ratio for HDFC Mid-Cap Opportunities Fund?",
            "conversation_id": "smoke-2",
        },
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "FACTUAL_ANSWER"
    assert "0.85%" in r2.json()["answer"]

    # Smoke Test 3: Recommendation Refusal
    r3 = client.post(
        "/v1/questions",
        json={"query": "Which is the best fund to buy?", "conversation_id": "smoke-3"},
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "POLICY_REFUSAL"


def test_phase3b_rollout_stage_gating_and_allowlist():
    # Set to INTERNAL_QA stage
    rollout_manager.set_stage(RolloutStage.INTERNAL_QA)
    rollout_manager.add_allowlist_user("qa_tester_1")

    # Unapproved user should receive 403 Forbidden
    r_blocked = client.post(
        "/v1/questions",
        json={
            "query": "What is the expense ratio for HDFC Mid-Cap?",
            "conversation_id": "r-1",
        },
        headers={"X-User-Id": "unauthorized_user"},
    )
    assert r_blocked.status_code == 403
    assert "restricted" in r_blocked.json()["detail"].lower()

    # Approved QA user is allowed
    r_allowed = client.post(
        "/v1/questions",
        json={
            "query": "What is the expense ratio for HDFC Mid-Cap Opportunities Fund?",
            "conversation_id": "r-2",
        },
        headers={"X-User-Id": "qa_tester_1"},
    )
    assert r_allowed.status_code == 200

    # Reset to General Availability
    rollout_manager.set_stage(RolloutStage.GENERAL_AVAILABILITY)


def test_phase3b_emergency_automated_rollback():
    # Trigger emergency rollback (Section 13.4)
    rollout_manager.trigger_emergency_rollback("Critical unverified claim reported")
    assert rollout_manager.is_emergency_refusal_mode is True

    # All queries should be blocked with 403 during emergency mode
    r_emergency = client.post(
        "/v1/questions",
        json={
            "query": "What is the expense ratio for HDFC Mid-Cap?",
            "conversation_id": "r-3",
        },
    )
    assert r_emergency.status_code == 403
    assert "emergency" in r_emergency.json()["detail"].lower()

    # Reset emergency mode
    rollout_manager.reset_emergency_mode()
    r_restored = client.post(
        "/v1/questions",
        json={
            "query": "What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
            "conversation_id": "r-4",
        },
    )
    assert r_restored.status_code == 200
