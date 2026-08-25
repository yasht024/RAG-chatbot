import time
import hashlib
import logging
from typing import Optional, Dict
from packages.contracts.schemas import FactualResponse, TerminalState

logger = logging.getLogger(__name__)


class CacheEntry:
    def __init__(self, response: FactualResponse, created_at: float, ttl_seconds: float):
        self.response = response
        self.created_at = created_at
        self.ttl_seconds = ttl_seconds

    def is_expired(self, now: float) -> bool:
        return (now - self.created_at) > self.ttl_seconds


class EvidenceAwareAnswerCache:
    """
    P3-REL-05: Answer cache keyed by (normalized_query, corpus_version, policy_version).
    - Automatically invalidated when corpus or policy version changes.
    - Applies short TTL for refusal states (P3-REL-06).
    """

    def __init__(self, factual_ttl_sec: float = 3600.0, refusal_ttl_sec: float = 60.0):
        self._store: Dict[str, CacheEntry] = {}
        self.factual_ttl_sec = factual_ttl_sec
        self.refusal_ttl_sec = refusal_ttl_sec
        self.hits = 0
        self.misses = 0

    def _make_key(self, query: str, corpus_version: str, policy_version: str) -> str:
        norm_query = query.strip().lower()
        raw = f"{norm_query}|{corpus_version}|{policy_version}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, query: str, corpus_version: str, policy_version: str) -> Optional[FactualResponse]:
        key = self._make_key(query, corpus_version, policy_version)
        now = time.time()
        entry = self._store.get(key)

        if entry is None:
            self.misses += 1
            return None

        if entry.is_expired(now):
            logger.debug(f"Cache key {key} expired. Removing.")
            del self._store[key]
            self.misses += 1
            return None

        self.hits += 1
        logger.debug(f"Cache HIT for query: '{query}'")
        return entry.response

    def put(
        self,
        query: str,
        corpus_version: str,
        policy_version: str,
        response: FactualResponse,
    ):
        # Do not cache temporary outage / error states
        if response.status == TerminalState.TEMPORARILY_UNAVAILABLE:
            return

        ttl = self.factual_ttl_sec if response.status == TerminalState.FACTUAL_ANSWER else self.refusal_ttl_sec
        key = self._make_key(query, corpus_version, policy_version)
        self._store[key] = CacheEntry(response, time.time(), ttl)
        logger.debug(f"Cached response for '{query}' with TTL {ttl}s")

    def invalidate_all(self):
        self._store.clear()
        logger.info("Answer cache completely invalidated.")
