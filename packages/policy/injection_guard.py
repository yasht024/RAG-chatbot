import re
from typing import Optional, Dict, Any


class PromptInjectionGuard:
    """
    Detects adversarial prompt injections in both user inputs and retrieved source passages.
    Prevents jailbreaks, system instruction overrides, and policy bypasses.
    """

    INJECTION_PATTERNS = [
        r"\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b",
        r"\bdisregard\s+(?:all\s+)?(?:rules|guidelines|system|policy)\b",
        r"\byou\s+are\s+now\s+(?:in\s+developer\s+mode|unrestricted|an\s+advisor|dan\b)\b",
        r"\boverride\s+(?:system|policy|security|guidelines)\b",
        r"\bsystem\s+prompt\s*:\b",
        r"\bact\s+as\s+(?:a\s+financial\s+advisor|an\s+unfiltered|jailbroken)\b",
        r"\bdo\s+anything\s+now\b",
    ]

    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]

    def scan_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Scans a text snippet for prompt injection attacks.
        Returns detection metadata if detected, else None.
        """
        for pat in self.patterns:
            match = pat.search(text)
            if match:
                return {
                    "injection_detected": True,
                    "matched_pattern": match.group(0),
                    "reason": "Prompt injection pattern detected in input text.",
                }
        return None

    def is_safe(self, text: str) -> bool:
        return self.scan_text(text) is None
