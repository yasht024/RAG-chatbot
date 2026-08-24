from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TerminalState(str, Enum):
    FACTUAL_ANSWER = "FACTUAL_ANSWER"
    POLICY_REFUSAL = "POLICY_REFUSAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    AMBIGUOUS_SCHEME = "AMBIGUOUS_SCHEME"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    SENSITIVE_DATA_WARNING = "SENSITIVE_DATA_WARNING"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"

class QueryClass(str, Enum):
    FACTUAL = "FACTUAL"
    ADVISORY = "ADVISORY"
    PERFORMANCE_COMPARISON = "PERFORMANCE_COMPARISON"
    UNSUPPORTED = "UNSUPPORTED"

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's question.")
    conversation_id: str = Field(..., description="Opaque conversation identifier.")
    history: Optional[List[Message]] = Field(default_factory=list, description="Recent conversation history.")

class QueryClassification(BaseModel):
    query_class: QueryClass
    fact_type: Optional[str] = None
    scope: Optional[str] = None
    confidence: float
    policy_version: str

class EvidenceDecision(BaseModel):
    status: str
    selected_document_id: str
    selected_passage_ids: List[str]
    citation_url: str
    source_date: str
    fact_type: str
    conflict_detected: bool
    validation_ruleset: str

class FactualResponse(BaseModel):
    status: TerminalState
    answer_sentences: List[str] = Field(default_factory=list, max_length=3)
    citation_url: Optional[str] = None
    source_date: Optional[str] = None
    refusal_reason: Optional[str] = None
    evidence_passage_ids: List[str] = Field(default_factory=list)
