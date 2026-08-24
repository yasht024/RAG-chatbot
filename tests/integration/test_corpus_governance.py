import pytest
from packages.corpus.lineage import DocumentLineageManager
from packages.corpus.conflicts import ConflictRegistry, ConflictStatus
from packages.corpus.manifest import CorpusManifestManager, ManifestStatus
from packages.corpus.quality_check import CorpusQualityChecker
from packages.policy.validation import validate_candidates

def test_document_lineage_supersession():
    lineage = DocumentLineageManager()
    lineage.register_relationship("doc_hdfc_midcap_2026_08", "doc_hdfc_midcap_2026_07")
    
    assert lineage.is_superseded("doc_hdfc_midcap_2026_07") is True
    assert lineage.is_superseded("doc_hdfc_midcap_2026_08") is False
    assert lineage.get_latest_successor("doc_hdfc_midcap_2026_07") == "doc_hdfc_midcap_2026_08"

    candidates = [
        {"passage_id": "old_p1", "document_id": "doc_hdfc_midcap_2026_07", "scheme_ids": ["hdfc_mid_cap"]},
        {"passage_id": "new_p1", "document_id": "doc_hdfc_midcap_2026_08", "scheme_ids": ["hdfc_mid_cap"]}
    ]
    filtered = lineage.filter_superseded_candidates(candidates)
    assert len(filtered) == 1
    assert filtered[0]["passage_id"] == "new_p1"

def test_conflict_registry_quarantine_and_resolution():
    registry = ConflictRegistry()
    
    # Record a conflict
    conflicting_passages = [
        {"passage_id": "p1", "normalized_text": "Exit load 1%", "source_url": "https://groww.in/p1"},
        {"passage_id": "p2", "normalized_text": "Exit load 2%", "source_url": "https://groww.in/p2"}
    ]
    record = registry.record_conflict("hdfc_mid_cap", "exit_load", conflicting_passages)
    assert record.status == ConflictStatus.QUARANTINED
    assert registry.is_quarantined("hdfc_mid_cap", "exit_load") is True
    
    # Validation should fail closed due to quarantine
    decision = validate_candidates(
        candidates=[{"passage_id": "p1", "scheme_ids": ["hdfc_mid_cap"], "fact_types": ["exit_load"], "normalized_text": "Exit load 1%"}],
        expected_scheme="hdfc_mid_cap",
        conflict_reg=registry
    )
    assert decision.status == "SOURCE_CONFLICT"

    # Operator resolves conflict
    registry.resolve_conflict("hdfc_mid_cap", "exit_load", "p1", "ops_admin", "Verified against AMC notice")
    assert registry.is_quarantined("hdfc_mid_cap", "exit_load") is False

def test_manifest_staging_approval_and_blue_green():
    manager = CorpusManifestManager()
    
    # Register staged manifest
    manifest = manager.register_manifest("m_v2.0", "2.0.0", schemes_count=35, documents_count=120)
    assert manifest.status == ManifestStatus.STAGED
    
    # Cannot publish unapproved manifest
    with pytest.raises(ValueError, match="Must be APPROVED"):
        manager.publish_blue_green("m_v2.0")
        
    # Approve manifest
    manager.approve_manifest("m_v2.0", approver="data_steward")
    assert manifest.status == ManifestStatus.APPROVED
    
    # Publish to Blue/Green slot
    active_slot = manager.publish_blue_green("m_v2.0")
    assert active_slot == "green"
    assert manager.active_manifest_id == "m_v2.0"
    
    # Publish next approved version
    m2 = manager.register_manifest("m_v2.1", "2.1.0", 35, 125)
    manager.approve_manifest("m_v2.1", approver="lead_engineer")
    next_slot = manager.publish_blue_green("m_v2.1")
    assert next_slot == "blue"
    assert manager.active_manifest_id == "m_v2.1"
    
    # Rollback drill
    rolled_back_id = manager.rollback()
    assert rolled_back_id == "m_v2.0"
    assert manager.active_slot == "green"

def test_quality_checker_source_links_and_regressions():
    valid_passages = [
        {
            "passage_id": "p1",
            "scheme_ids": ["hdfc_mid_cap"],
            "fact_types": ["expense_ratio"],
            "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap"
        }
    ]
    
    is_valid, errors = CorpusQualityChecker.validate_source_links(valid_passages)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid domain
    invalid_passages = [
        {
            "passage_id": "p2",
            "scheme_ids": ["hdfc_mid_cap"],
            "fact_types": ["expense_ratio"],
            "source_url": "https://unauthorized-blog.com/funds"
        }
    ]
    is_valid, errors = CorpusQualityChecker.validate_source_links(invalid_passages)
    assert is_valid is False
    assert "unapproved domain" in errors[0]

    # Coverage regression test
    is_cov_valid, cov_errors = CorpusQualityChecker.detect_coverage_regressions(
        passages=valid_passages,
        expected_schemes={"hdfc_mid_cap", "hdfc_flexi_cap"},
        baseline_scheme_count=2
    )
    assert is_cov_valid is False
    assert "Missing 1 expected scheme(s)" in cov_errors[0]
