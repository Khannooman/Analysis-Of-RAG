from dataclasses import dataclass
from typing import Optional, Dict, List, str, Any

@dataclass
class VectorSearchResult:
    """Data class for vector search results."""
    message: str
    results: Optional[List[Dict[str, Any]]] = None