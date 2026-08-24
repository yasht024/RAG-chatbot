import pytest
from packages.resilience.token_limiter import LLMRateLimiter
from packages.cache.answer_cache import EvidenceAwareAnswerCache
from packages.contracts.schemas import FactualResponse, TerminalState, QueryRequest
from services.assistant_api.orchestrator import Orchestrator
from services.assistant_api.llm_client import LLMClient

def test_llm_rate_limiter_rpm_and_tpm():
    # Test strict limits: 30 RPM, 8000 TPM
    limiter = LLMRateLimiter(max_rpm=3, max_rpd=1000, max_tpm=500, max_tpd=200000)
    
    # 1st request
    has_cap, err = limiter.check_capacity(100)
    assert has_cap is True
    limiter.record_usage(100)
    
    # 2nd request
    has_cap, err = limiter.check_capacity(200)
    assert has_cap is True
    limiter.record_usage(200)
    
    # 3rd request
    has_cap, err = limiter.check_capacity(100)
    assert has_cap is True
    limiter.record_usage(100)
    
    # 4th request exceeds RPM limit of 3
    has_cap, err = limiter.check_capacity(50)
    assert has_cap is False
    assert "RPM limit exceeded" in err

def test_llm_rate_limiter_tpm_exhaustion():
    limiter = LLMRateLimiter(max_rpm=30, max_rpd=1000, max_tpm=300, max_tpd=200000)
    limiter.record_usage(250)
    
    # Exceeds 300 TPM (250 + 100 > 300)
    has_cap, err = limiter.check_capacity(100)
    assert has_cap is False
    assert "TPM limit exceeded" in err

def test_evidence_aware_answer_cache_version_invalidation():
    cache = EvidenceAwareAnswerCache(factual_ttl_sec=100.0, refusal_ttl_sec=10.0)
    
    resp_v1 = FactualResponse(
        status=TerminalState.FACTUAL_ANSWER,
        answer_sentences=["Expense ratio is 0.85%."],
        citation_url="https://groww.in/hdfc-mid-cap"
    )
    
    query = "What is the expense ratio for HDFC Mid-Cap?"
    cache.put(query, corpus_version="2.0.0", policy_version="2026-08-23.1", response=resp_v1)
    
    # Cache hit with matching versions
    cached = cache.get(query, corpus_version="2.0.0", policy_version="2026-08-23.1")
    assert cached is not None
    assert cached.answer_sentences == ["Expense ratio is 0.85%."]
    assert cache.hits == 1
    
    # Cache miss when corpus version updates to 2.1.0 (Automatic Invalidation)
    assert cache.get(query, corpus_version="2.1.0", policy_version="2026-08-23.1") is None
    
    # Cache miss when policy version updates to 2026-08-24.1
    assert cache.get(query, corpus_version="2.0.0", policy_version="2026-08-24.1") is None

def test_orchestrator_cache_hit_avoids_recomputation():
    orch = Orchestrator()
    request = QueryRequest(
        query="What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
        conversation_id="cache-test-1"
    )
    
    # 1st execution: Miss, runs retrieval & caches
    resp1 = orch.process_query(request)
    assert resp1.status == TerminalState.FACTUAL_ANSWER
    assert orch.answer_cache.hits == 0
    
    # 2nd execution: HIT directly from cache
    resp2 = orch.process_query(request)
    assert resp2.status == TerminalState.FACTUAL_ANSWER
    assert resp2.answer_sentences == resp1.answer_sentences
    assert orch.answer_cache.hits == 1

def test_llm_client_quota_fallback():
    client = LLMClient()
    # Mock quota exceeded
    client.rate_limiter.max_rpm = 0
    
    # Even if quota is exhausted, it gracefully falls back to local template without crashing
    answer = client.generate_descriptive_answer("investment_objective", "Sample objective passage")
    assert "investment objective" in answer.lower()
