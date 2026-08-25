from fastapi import FastAPI, HTTPException, Request, Header
from packages.contracts.schemas import QueryRequest
from services.assistant_api.orchestrator import Orchestrator
from services.assistant_api.renderer import render_response
from services.assistant_api.diagnostics import router as diagnostics_router
from services.assistant_api.middleware import CorrelationIdMiddleware, RateLimitMiddleware, redact_pii, IDEMPOTENCY_CACHE
from packages.rollout.stage_manager import RolloutStageManager, RolloutStage
from typing import Optional

app = FastAPI(title="Mutual Fund FAQ Assistant - Phase 3 Production")
orchestrator = Orchestrator()
rollout_manager = RolloutStageManager(initial_stage=RolloutStage.GENERAL_AVAILABILITY)

from fastapi.middleware.cors import CORSMiddleware

# Register Middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnostics_router, prefix="/v1/internal", tags=["Internal"])

@app.post("/v1/questions")
async def ask_question(
    request: QueryRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    try:
        # Rollout stage access check (P3B-07, P3B-08)
        access_decision = rollout_manager.evaluate_request_access(user_id=user_id)
        if not access_decision.allowed:
            raise HTTPException(status_code=403, detail=access_decision.reason)

        # Idempotency Check
        if idempotency_key and idempotency_key in IDEMPOTENCY_CACHE:
            return IDEMPOTENCY_CACHE[idempotency_key]
            
        # PII Redaction
        request.query = redact_pii(request.query)
        
        internal_response = orchestrator.process_query(request)
        final_payload = render_response(internal_response)
        
        # Cache Response
        if idempotency_key:
            IDEMPOTENCY_CACHE[idempotency_key] = final_payload
            
        return final_payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """
    P3B-02: Production readiness health telemetry with manifest, policy,
    circuit breaker, and rate limit diagnostics.
    """
    from services.assistant_api.generator import llm

    return {
        "status": "ok", 
        "version": "3.0.0-rc1",
        "policy_version": orchestrator.policy_version,
        "corpus": {
            "version": orchestrator.corpus_version,
            "is_connected": True,
            "mock_corpus_size": len(orchestrator.keyword_search.search("a", limit=100))
        },
        "rollout": {
            "stage": rollout_manager.stage.value,
            "emergency_refusal_mode": rollout_manager.is_emergency_refusal_mode
        },
        "resilience": {
            "vector_breaker_state": orchestrator.vector_circuit_breaker.state.value,
            "keyword_breaker_state": orchestrator.keyword_circuit_breaker.state.value,
            "cache_hits": orchestrator.answer_cache.hits,
            "cache_misses": orchestrator.answer_cache.misses
        },
        "llm_limits": {
            "max_rpm": llm.rate_limiter.max_rpm,
            "max_rpd": llm.rate_limiter.max_rpd,
            "max_tpm": llm.rate_limiter.max_tpm,
            "max_tpd": llm.rate_limiter.max_tpd
        }
    }


