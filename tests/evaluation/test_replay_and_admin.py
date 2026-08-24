import pytest
from fastapi.testclient import TestClient
from services.assistant_api.main import app
from services.assistant_api.orchestrator import Orchestrator
from packages.evaluation.replay import ReplayEvaluator
from packages.corpus.conflicts import ConflictRegistry, ConflictStatus

client = TestClient(app)

def test_admin_diagnostics_conflicts_and_manifests():
    # 1. Test Manifests status endpoint
    r_man = client.get("/v1/internal/manifests")
    assert r_man.status_code == 200
    assert r_man.json()["status"] == "success"
    assert r_man.json()["active_slot"] in ["blue", "green"]

    # 2. Test Conflicts listing
    r_conf = client.get("/v1/internal/conflicts")
    assert r_conf.status_code == 200
    assert r_conf.json()["status"] == "success"

def test_replay_evaluator_drift_and_regressions():
    orch_base = Orchestrator()
    orch_cand = Orchestrator()
    
    evaluator = ReplayEvaluator(orch_base, orch_cand)
    
    test_data = [
        {"query": "What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?"},
        {"query": "What is the expense ratio for HDFC Mid-Cap Opportunities Fund?"},
        {"query": "Should I buy this fund?"}
    ]
    
    report = evaluator.run_replay_comparison(test_data)
    assert report["total_queries"] == 3
    assert report["agreements"] == 3
    assert report["agreement_rate"] == 1.0
    assert report["regressions_count"] == 0
