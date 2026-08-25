from tests.integration.test_slice_e2e import (
    test_health_check,
    test_factual_answer_minimum_sip,
    test_policy_refusal_recommendation,
    test_insufficient_evidence_unsupported,
)

print("Running test_health_check...")
test_health_check()
print("Running test_factual_answer_minimum_sip...")
test_factual_answer_minimum_sip()
print("Running test_policy_refusal_recommendation...")
test_policy_refusal_recommendation()
print("Running test_insufficient_evidence_unsupported...")
test_insufficient_evidence_unsupported()
print("All tests passed!")
