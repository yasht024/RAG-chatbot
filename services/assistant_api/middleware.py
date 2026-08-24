import uuid
import re
from typing import Dict, Any, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

# Very simple in-memory stores for mock Phase 2B
IDEMPOTENCY_CACHE: Dict[str, Any] = {}
RATE_LIMIT_STORE: Dict[str, list] = {}

def redact_pii(text: str) -> str:
    """Mock PII redactor."""
    if not text:
        return text
    # Very simple PAN regex mock: 5 chars, 4 digits, 1 char
    text = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[REDACTED_PAN]', text)
    # Phone numbers mock (simple 10 digit)
    text = re.sub(r'\b\d{10}\b', '[REDACTED_PHONE]', text)
    return text

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Simple sliding window (10 requests per 60 seconds)
        now = time.time()
        window = 60
        limit = 10
        
        if client_ip not in RATE_LIMIT_STORE:
            RATE_LIMIT_STORE[client_ip] = []
            
        requests = RATE_LIMIT_STORE[client_ip]
        # Clean old
        requests = [t for t in requests if now - t < window]
        
        if len(requests) >= limit:
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})
            
        requests.append(now)
        RATE_LIMIT_STORE[client_ip] = requests
        
        return await call_next(request)

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST":
            return await call_next(request)
            
        idem_key = request.headers.get("Idempotency-Key")
        if not idem_key:
            return await call_next(request)
            
        if idem_key in IDEMPOTENCY_CACHE:
            return JSONResponse(
                content=IDEMPOTENCY_CACHE[idem_key],
                headers={"X-Cache": "HIT"}
            )
            
        response = await call_next(request)
        
        # We cannot easily read the response body in BaseHTTPMiddleware if it's streaming, 
        # but in FastAPI we will intercept this at the route level for caching. 
        # For simplicity in this mock, the caching happens in the route itself.
        # So we just mark the state.
        request.state.idem_key = idem_key
        return response
