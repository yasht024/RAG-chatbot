import httpx
from typing import Dict, Any, Optional


class PolicyServiceClient:
    """
    Client for the standalone Policy Microservice.
    Enforces fail-closed behavior on network timeouts or errors.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 5.0  # Strict SLA timeout

    async def _safe_post(self, endpoint: str, payload: dict) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}{endpoint}", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError:
            # Fail closed on network/connection issues
            return {
                "status": "POLICY_REFUSAL",
                "refusal_reason": "SERVICE_UNAVAILABLE",
                "answer_sentences": [
                    "The policy verification service is currently unavailable. Please try again later."
                ],
                "citation_url": None,
            }
        except httpx.HTTPStatusError:
            # Fail closed on 5xx or 4xx errors
            return {
                "status": "POLICY_REFUSAL",
                "refusal_reason": "SERVICE_ERROR",
                "answer_sentences": ["An error occurred during policy verification. Please try again later."],
                "citation_url": None,
            }

    async def scan_query(self, query: str) -> Dict[str, Any]:
        return await self._safe_post("/v1/policy/scan", {"query": query})

    async def classify_query(self, query: str) -> Dict[str, Any]:
        return await self._safe_post("/v1/policy/classify", {"query": query})

    async def resolve_scheme(self, query: str) -> Dict[str, Any]:
        return await self._safe_post("/v1/policy/resolve", {"query": query})

    async def render_refusal(
        self,
        query_class: str,
        reason_code: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "query_class": query_class,
            "reason_code": reason_code,
            "query": query,
        }
        return await self._safe_post("/v1/policy/refusal", payload)
