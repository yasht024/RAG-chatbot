import pytest
import time
from packages.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
)
from packages.resilience.retry import retry_with_backoff
from services.assistant_api.orchestrator import Orchestrator
from services.assistant_api.llm_client import LLMClient
from packages.contracts.schemas import QueryRequest, TerminalState


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.2, name="test_cb")

    def flaky_fn(should_fail=True):
        if should_fail:
            raise ValueError("Service error")
        return "success"

    assert cb.state == CircuitState.CLOSED

    # 1st failure
    with pytest.raises(ValueError):
        cb.call(flaky_fn, True)
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1

    # 2nd failure -> trips breaker
    with pytest.raises(ValueError):
        cb.call(flaky_fn, True)
    assert cb.state == CircuitState.OPEN

    # When OPEN, immediately raises CircuitBreakerOpenException without calling fn
    with pytest.raises(CircuitBreakerOpenException):
        cb.call(flaky_fn, False)

    # Wait for recovery timeout -> transitions to HALF_OPEN on next call
    time.sleep(0.25)
    result = cb.call(flaky_fn, False)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_retry_with_backoff():
    attempts = 0

    def transient_fn():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("Transient network failure")
        return "recovered"

    result = retry_with_backoff(transient_fn, max_retries=3, initial_delay=0.01, backoff_factor=1.5)
    assert result == "recovered"
    assert attempts == 3


def test_llm_circuit_breaker_and_network_fallback():
    client = LLMClient()
    client.set_test_mode(force_network_error=True)

    # Even when external LLM API throws network errors, it gracefully falls back
    answer = client.generate_descriptive_answer("investment_objective", "Sample passage text")
    assert "investment objective" in answer.lower()


def test_orchestrator_degrades_to_lexical_when_vector_fails():
    orch = Orchestrator()

    # Force vector search to fail
    def failing_vector_search(*args, **kwargs):
        raise TimeoutError("Vector index timed out")

    orch.vector_search.search = failing_vector_search

    request = QueryRequest(
        query="What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
        conversation_id="resilience-test-1",
    )

    response = orch.process_query(request)
    assert response.status == TerminalState.FACTUAL_ANSWER
    assert "₹100" in response.answer_sentences[0]


def test_orchestrator_fails_closed_when_all_retrieval_fails():
    orch = Orchestrator()
    # Force both keyword and vector searches to fail
    orch.keyword_search.search = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("DB down"))
    orch.vector_search.search = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("Vector down"))

    request = QueryRequest(
        query="What is the minimum SIP amount for HDFC Mid-Cap Opportunities Fund?",
        conversation_id="resilience-test-2",
    )

    response = orch.process_query(request)
    assert response.status == TerminalState.TEMPORARILY_UNAVAILABLE
    assert "temporarily unavailable" in response.refusal_reason.lower()
