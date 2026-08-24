from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class RetrievalClient(ABC):
    """Abstract base class for search retrieval implementations."""
    
    @abstractmethod
    def search(
        self, 
        query: str, 
        scheme_id: Optional[str] = None, 
        plan: str = "Direct", 
        option: str = "Growth", 
        limit: int = 20,
        document_types: Optional[List[str]] = None,
        fact_type: Optional[str] = None,
        amc_level: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute a search and return a list of passage candidates.
        """
        pass
