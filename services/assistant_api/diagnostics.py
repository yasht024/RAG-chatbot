from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from packages.retrieval.search import InMemoryKeywordSearch, InMemoryVectorSearch
from packages.retrieval.fusion import reciprocal_rank_fusion
from packages.retrieval.router import DocumentRouter
from packages.policy.validation import default_conflict_registry
from packages.corpus.manifest import CorpusManifestManager

router = APIRouter()

kw_search = InMemoryKeywordSearch()
vec_search = InMemoryVectorSearch()
manifest_mgr = CorpusManifestManager()
manifest_mgr.register_manifest("m_v2.0", "2.0.0", schemes_count=35, documents_count=120)
manifest_mgr.approve_manifest("m_v2.0", "system_init")
manifest_mgr.publish_blue_green("m_v2.0")

@router.get("/retrieval-diagnostics")
async def retrieval_diagnostics(
    query: str, 
    fact_type: str, 
    scheme_id: str = None, 
    amc_level: bool = False
) -> Dict[str, Any]:
    """
    P2B-RET-06: Retrieval diagnostics endpoint for authorized operators.
    Returns ranked passage IDs without public exposure.
    """
    allowed_docs = DocumentRouter.get_document_types_for_fact(fact_type)
    
    kw_res = kw_search.search(query, scheme_id, document_types=allowed_docs, fact_type=fact_type, amc_level=amc_level)
    vec_res = vec_search.search(query, scheme_id, document_types=allowed_docs, fact_type=fact_type, amc_level=amc_level)
    
    fused = reciprocal_rank_fusion(kw_res, vec_res)
    
    return {
        "status": "success",
        "query": query,
        "fact_type": fact_type,
        "document_routing": allowed_docs,
        "ranked_passages": [p["passage_id"] for p in fused]
    }

@router.get("/conflicts")
async def list_quarantined_conflicts():
    """P3-COR-08: Lists all quarantined source conflicts requiring operator review."""
    conflicts = default_conflict_registry.list_quarantined_conflicts()
    return {
        "status": "success",
        "quarantined_count": len(conflicts),
        "conflicts": [c.dict() for c in conflicts]
    }

@router.post("/conflicts/resolve")
async def resolve_conflict_endpoint(
    scheme_id: str = Body(...),
    fact_type: str = Body(...),
    selected_passage_id: str = Body(...),
    operator: str = Body(...),
    reason: str = Body(...)
):
    """P3-COR-08: Allows operator to resolve a quarantined conflict with an audit trail."""
    try:
        record = default_conflict_registry.resolve_conflict(
            scheme_id=scheme_id,
            fact_type=fact_type,
            selected_passage_id=selected_passage_id,
            operator_name=operator,
            reason=reason
        )
        return {"status": "success", "record": record.dict()}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/manifests")
async def get_manifests_status():
    """P3-COR-08: Inspects active manifest and serving slot."""
    active = manifest_mgr.get_active_manifest()
    return {
        "status": "success",
        "active_slot": manifest_mgr.active_slot,
        "active_manifest": active.dict() if active else None,
        "previous_manifest_id": manifest_mgr.previous_active_manifest_id
    }

