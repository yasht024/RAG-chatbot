import re
from typing import Optional, Dict, Any

class PrivacyGuard:
    """
    Scans user queries for sensitive PII and financial credentials before retrieval or generation.
    Enforces strict data boundaries with zero PII echoing.
    """
    def __init__(self):
        self.pan_pattern = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
        self.aadhaar_pattern = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
        self.otp_pattern = re.compile(r"\b(?:otp|one[- ]time password|code)(?:\s+is|\s*[:\s#])*\s*\d{4,6}\b", re.IGNORECASE)
        self.bank_acc_pattern = re.compile(r"\b(?:account|acct|acc)(?:\s+number|\s*[:\s#])*\s*\d{9,18}\b", re.IGNORECASE)
        self.password_pattern = re.compile(r"\b(?:password|pwd|pin)[:\s]*[^\s]+\b", re.IGNORECASE)


    def scan_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Returns detection metadata if sensitive data is found, otherwise None.
        """
        detections = []
        
        if self.pan_pattern.search(query):
            detections.append("PAN_NUMBER")
        if self.aadhaar_pattern.search(query):
            detections.append("AADHAAR_NUMBER")
        if self.otp_pattern.search(query):
            detections.append("OTP_CODE")
        if self.bank_acc_pattern.search(query):
            detections.append("BANK_ACCOUNT")
        if self.password_pattern.search(query):
            detections.append("CREDENTIAL")

        if detections:
            return {
                "sensitive_data_detected": True,
                "categories": detections,
                "terminal_status": "SENSITIVE_DATA_WARNING",
                "message": "We detected sensitive financial information (such as a PAN, Aadhaar, OTP, or account credential). For your safety, this assistant cannot process personal account credentials. Please use the official secure Groww or AMC customer portal."
            }
            
        return None
