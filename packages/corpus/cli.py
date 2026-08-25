import argparse
from packages.corpus.manifest import CorpusManifestManager
from packages.corpus.conflicts import ConflictRegistry


def create_admin_cli(manifest_mgr: CorpusManifestManager, conflict_reg: ConflictRegistry):
    parser = argparse.ArgumentParser(description="Corpus & Conflict Administration CLI (P3-COR-08)")
    subparsers = parser.add_subparsers(dest="command", help="Available admin commands")

    # Command: list-conflicts
    subparsers.add_parser("list-conflicts", help="List all quarantined conflicts")

    # Command: resolve-conflict
    resolve_parser = subparsers.add_parser("resolve-conflict", help="Resolve a quarantined conflict")
    resolve_parser.add_argument("--scheme", required=True, help="Scheme identifier")
    resolve_parser.add_argument("--fact-type", required=True, help="Fact type")
    resolve_parser.add_argument("--passage-id", required=True, help="Winning passage ID")
    resolve_parser.add_argument("--operator", required=True, help="Operator name")
    resolve_parser.add_argument("--reason", required=True, help="Resolution rationale")

    # Command: manifests
    subparsers.add_parser("manifests", help="Inspect active and staged manifests")

    # Command: approve-manifest
    approve_parser = subparsers.add_parser("approve-manifest", help="Approve a staged manifest")
    approve_parser.add_argument("--manifest-id", required=True, help="Manifest ID")
    approve_parser.add_argument("--approver", required=True, help="Approver name")

    # Command: publish-blue-green
    publish_parser = subparsers.add_parser("publish-blue-green", help="Switch Blue/Green serving slot")
    publish_parser.add_argument("--manifest-id", required=True, help="Approved Manifest ID")

    # Command: rollback
    subparsers.add_parser("rollback", help="Execute immediate rollback to previous manifest")

    return parser


if __name__ == "__main__":
    from packages.policy.validation import default_conflict_registry

    manifest_manager = CorpusManifestManager()
    parser = create_admin_cli(manifest_manager, default_conflict_registry)
    args = parser.parse_args()
    print(f"Executing CLI command: {args.command}")
