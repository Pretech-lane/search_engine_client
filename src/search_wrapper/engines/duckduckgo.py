import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from .base import BaseSearchEngine

class DuckDuckGoSearch(BaseSearchEngine):
    def __init__(self):
        # We mimic a browser to avoid being blocked
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        # Initialize client
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0, follow_redirects=True)

    async def search(self, query: str, total_search_result: int = 10, total_image_results: int = 0) -> Dict[str, Any]:
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}

        try:
            # We use data= for form submission on the HTML version
            response = await self.client.post(url, data=data)
            response.raise_for_status()
        except httpx.RequestError as e:
            print(f"DuckDuckGo Request Failed: {e}")
            return {"data": [], "images": []}

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Parse DuckDuckGo HTML structure
        # Note: These selectors are fragile and depend on DDG's current HTML structure
        raw_results = soup.find_all("div", class_="result")[:total_search_result]

        for result in raw_results:
            link_tag = result.find("a", class_="result__a")
            if not link_tag:
                continue
            
            heading = link_tag.get_text().strip()
            page_url = link_tag.get("href")
            
            snippet_tag = result.find("a", class_="result__snippet")
            meta_description = snippet_tag.get_text().strip() if snippet_tag else ""

            results.append({
                "title": heading,
                "link": page_url,
                "snippet": meta_description,
                "image_url": None 
            })

        # --- Image Extraction Logic ---
        # Only run if we actually found results
        if results:
            tasks = [self._extract_image_from_page(res["link"]) for res in results]
            images_found = await asyncio.gather(*tasks, return_exceptions=True)

            image_urls_list = []
            for i, img_url in enumerate(images_found):
                # Check if we got a valid string back (not an exception or None)
                if isinstance(img_url, str) and img_url:
                    results[i]["image_url"] = img_url
                    image_urls_list.append(img_url)
        else:
            image_urls_list = []

        return {
            "data": results,
            "images": image_urls_list
        }

    async def _extract_image_from_page(self, page_url: str) -> Optional[str]:
        """
        Visits the page to find og:image.
        """
        try:
            # Short timeout because visiting many sites takes time
            response = await self.client.get(page_url, timeout=5.0)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try OG Image first
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image.get("content")
            
            return None
        except Exception:
            return None

    async def close(self):
        await self.client.aclose()

    # --- THE MISSING PART IS HERE ---
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()