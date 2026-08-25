from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from packages.policy.privacy_guard import PrivacyGuard
from packages.policy.classifier import QueryClassifier
from packages.policy.resolver import SchemeResolver
from packages.policy.refusal_renderer import RefusalRenderer

app = FastAPI(title="Policy Service", version="1.0.0")

guard = PrivacyGuard()
classifier = QueryClassifier()
resolver = SchemeResolver()
renderer = RefusalRenderer()


class QueryPayload(BaseModel):
    query: str


class RefusalPayload(BaseModel):
    query_class: str
    reason_code: Optional[str] = None
    query: Optional[str] = None


@app.post("/v1/policy/scan")
async def scan_query(payload: QueryPayload) -> Dict[str, Any]:
    res = guard.scan_query(payload.query)
    # The guard returns None if clean, or a dict if sensitive data is found
    if res is None:
        return {"status": "CLEAN"}
    return res


@app.post("/v1/policy/classify")
async def classify_query(payload: QueryPayload) -> Dict[str, Any]:
    res = classifier.classify_query(payload.query)
    return res


@app.post("/v1/policy/resolve")
async def resolve_scheme(payload: QueryPayload) -> Dict[str, Any]:
    res = resolver.resolve_scheme(payload.query)
    return res


@app.post("/v1/policy/refusal")
async def render_refusal(payload: RefusalPayload) -> Dict[str, Any]:
    res = renderer.render_refusal(
        query_class=payload.query_class,
        reason_code=payload.reason_code,
        query=payload.query,
    )
    return res
