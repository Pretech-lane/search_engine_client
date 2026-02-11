import asyncio
import os
import httpx
from typing import Optional, Dict, Any
from .base import BaseSearchEngine 

class GoogleSearchFromSerper(BaseSearchEngine):
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://google.serper.dev"
        
        # Priority: Argument > Environment Variable
        self.api_key = api_key or os.getenv("GOOGLE_SERPER_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API Key missing. Pass `api_key` to init or set 'GOOGLE_SERPER_API_KEY' environment variable."
            )

        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Initialize a persistent client session
        self.client = httpx.AsyncClient(
            base_url=self.base_url, 
            headers=self.headers, 
            timeout=30.0
        )

    async def search(self, query: str, total_search_result: int = 10, total_image_results: int = 10) -> Dict[str, Any]:
        # Run text and image search concurrently
        tasks = [
            self._fetch_text(query, total_search_result),
            self._fetch_images(query, total_image_results)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Unpack results
        text_data = results[0]
        image_data = results[1]

        
        # If an error occurred, we log it or return it so you can see it.
        if isinstance(text_data, Exception):
            print(f"Error fetching text: {text_data}")
            text_data = {} # Safety fallback
            
        if isinstance(image_data, Exception):
            print(f"Error fetching images: {image_data}")
            image_data = {} # Safety fallback

        return {
            "data": text_data.get("organic", []),
            "images": image_data.get("images", [])
        }

    async def _fetch_text(self, query: str, count: int):
        payload = {"q": query, "num": count}
        # Note: endpoint is relative to base_url
        response = await self.client.post("/search", json=payload)
        response.raise_for_status()
        return response.json()

    async def _fetch_images(self, query: str, count: int):
        payload = {"q": query, "num": count}
        response = await self.client.post("/images", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()