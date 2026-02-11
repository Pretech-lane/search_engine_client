from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSearchEngine(ABC):
    """Abstract base class for all search engines."""

    @abstractmethod
    async def search(self, query: str, total_search_result: int, total_image_results: int) -> Dict[str, Any]:
        """Execute search and return standardized results."""
        pass

    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        pass