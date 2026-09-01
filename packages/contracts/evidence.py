from pydantic import BaseModel
from typing import Optional


class EvidenceItem(BaseModel):
    scheme_id: str
    scheme_name: Optional[str] = None
    plan: Optional[str] = None
    option: Optional[str] = None
    fact_type: str
    value: str
    source_org: str
    source_type: str
    source_url: str
    document_name: str
    publication_date: Optional[str] = None
    effective_date: Optional[str] = None
    page: Optional[int] = None
    approved: bool
    confidence: str  # "verified" | "unverified"
