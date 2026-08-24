from typing import Dict, Any

class RefusalRenderer:
    """
    Renders standardized, product-approved refusal responses with structured educational links.
    """
    def __init__(self):
        self.amfi_educational_link = "https://www.amfiindia.com/investor-corner"

    def _is_hindi(self, query: str) -> bool:
        if not query:
            return False
        # Simple heuristic: presence of Devnagari characters
        return any('\u0900' <= c <= '\u097F' for c in query)

    def render_refusal(self, query_class: str, reason_code: str = None, query: str = None) -> Dict[str, Any]:
        is_hindi = self._is_hindi(query)
        if query_class == "ADVISORY" or reason_code == "ADVISORY_PROHIBITED":
            if is_hindi:
                answer_sentences = [
                    "मैं म्यूचुअल फंड योजनाओं के बारे में सत्यापित तथ्य प्रदान कर सकता हूँ, लेकिन मैं निवेश सलाह या सिफारिशें नहीं दे सकता।",
                    f"सामान्य निवेशक शिक्षा और म्यूचुअल फंड दिशानिर्देशों के लिए, कृपया आधिकारिक AMFI पोर्टल देखें: {self.amfi_educational_link}"
                ]
            else:
                answer_sentences = [
                    "I can provide verified facts about mutual fund schemes, but I cannot provide investment advice or recommendations.",
                    f"For general investor education and mutual fund guidelines, please refer to the official AMFI portal: {self.amfi_educational_link}"
                ]
            return {
                "status": "POLICY_REFUSAL",
                "answer_sentences": answer_sentences,
                "citation_url": None,
                "refusal_reason": "ADVISORY_PROHIBITED"
            }

        if query_class == "PERFORMANCE_COMPARISON" or reason_code == "PERFORMANCE_RANKING_PROHIBITED":
            if is_hindi:
                answer_sentences = [
                    "मैं म्यूचुअल फंड के प्रदर्शन के आंकड़ों की तुलना, भविष्यवाणी या रैंकिंग नहीं कर सकता।",
                    "मैं केवल तथ्यात्मक योजना विवरण या आधिकारिक फैक्टशीट में स्पष्ट रूप से प्रकाशित एकल प्रदर्शन मूल्य प्रदान कर सकता हूँ।"
                ]
            else:
                answer_sentences = [
                    "I cannot rank, predict, or compare mutual fund performance figures across funds.",
                    "I can only provide factual scheme details or single performance values explicitly published in the official factsheet."
                ]
            return {
                "status": "POLICY_REFUSAL",
                "answer_sentences": answer_sentences,
                "citation_url": None,
                "refusal_reason": "PERFORMANCE_RANKING_PROHIBITED"
            }

        if reason_code == "UNSUPPORTED_PLAN":
            if is_hindi:
                answer_sentences = [
                    "मेरे पास इस योजना के समर्थित डायरेक्ट, रेगुलर, ग्रोथ और IDCW वेरिएंट के लिए ही सत्यापित तथ्यात्मक जानकारी है।"
                ]
            else:
                answer_sentences = [
                    "I only have verified factual information for the supported Direct, Regular, Growth, and IDCW variants of this scheme."
                ]
            return {
                "status": "POLICY_REFUSAL",
                "answer_sentences": answer_sentences,
                "citation_url": None,
                "refusal_reason": "UNSUPPORTED_PLAN"
            }

        if is_hindi:
            answer_sentences = [
                "मैं इस प्रश्न का उत्तर देने में असमर्थ हूँ क्योंकि यह मेरे तथ्यों-के-दायरे से बाहर है।"
            ]
        else:
            answer_sentences = [
                "I am unable to answer this question as it falls outside my facts-only scope."
            ]
        return {
            "status": "POLICY_REFUSAL",
            "answer_sentences": answer_sentences,
            "citation_url": None,
            "refusal_reason": "OUT_OF_SCOPE"
        }
