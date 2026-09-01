import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import urllib.request


class AllowlistViolationError(Exception):
    pass


class Fetcher:
    def __init__(self, sources_path: Path = None, snapshot_dir: Path = None):
        if sources_path is None:
            sources_path = Path(__file__).parents[2] / "data" / "catalog" / "sources.json"
        if snapshot_dir is None:
            snapshot_dir = Path(__file__).parents[2] / "data" / "fixtures" / "raw_sources"

        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        with open(sources_path, "r", encoding="utf-8") as f:
            self.sources_config = json.load(f)

        self.allowed_domains = set(self.sources_config.get("allowed_domains", []))

    def validate_url(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain not in self.allowed_domains:
            raise AllowlistViolationError(f"URL domain '{domain}' is not in allowed_domains: {self.allowed_domains}")
        return True

    def fetch_and_snapshot(self, url: str, raw_html_content: str = None) -> dict:
        """
        Fetches HTML from URL or uses provided raw_html_content (for testing/mocking),
        validates allowlist, computes SHA-256 hash, and saves to snapshot storage.
        """
        if raw_html_content is None:
            self.validate_url(url)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MutualFundFAQAssistant/1.0)"})
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_html_content = response.read().decode("utf-8")

        content_bytes = raw_html_content.encode("utf-8")
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        # Save snapshot file
        filename = f"{content_hash}.html"
        snapshot_path = self.snapshot_dir / filename
        with open(snapshot_path, "w", encoding="utf-8") as f:
            f.write(raw_html_content)

        return {
            "canonical_url": url,
            "source_domain": urlparse(url).netloc,
            "content_hash": f"sha256:{content_hash}",
            "snapshot_path": str(snapshot_path),
            "raw_html": raw_html_content,
        }
