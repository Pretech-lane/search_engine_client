import asyncio
import urllib.parse
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page
from .base import BaseSearchEngine

class BingSearch(BaseSearchEngine):
    def __init__(self, headless: bool = True):
        self.base_url = "https://www.bing.com"
        self.headless = headless
        self.playwright = None
        self.browser = None
        # File types to search for if requested
        self.file_types = ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "csv"]

    async def _ensure_browser(self):
        """Lazy loads the browser instance."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=self.headless)

    async def search(self, query: str, total_search_result: int = 10, total_image_results: int = 0) -> Dict[str, Any]:
        await self._ensure_browser()
        
        # We use a single context (like an incognito window) for this search
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Fetch Organic Results
            organic_results = await self._fetch_organic(page, query, total_search_result)
            
            # 2. Fetch Images (if requested)
            image_results = []
            if total_image_results > 0:
                image_results = await self._fetch_images(context, query, total_image_results)

            # 3. (Optional) Fetch Files - specific to your use case
            # I included this logic since it was in your original code
            file_results = await self._fetch_files(context, query)

            return {
                "data": organic_results,
                "images": image_results,
                "files": file_results
            }
        finally:
            await context.close()

    async def _fetch_organic(self, page: Page, query: str, count: int) -> List[Dict[str, Any]]:
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/search?q={encoded_query}"
        
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            content = await page.content()
        except Exception as e:
            print(f"Bing organic search failed: {e}")
            return []

        soup = BeautifulSoup(content, "html.parser")
        results = []
        
        # Bing selectors (li.b_algo is standard, but dynamic)
        raw_results = soup.find_all("li", class_="b_algo")[:count]

        for result in raw_results:
            h2 = result.find("h2")
            if not h2: continue
            
            a_tag = h2.find("a")
            if not a_tag: continue
            
            link = a_tag.get("href")
            title = a_tag.get_text().strip()
            
            snippet_tag = result.find("p")
            snippet = snippet_tag.get_text().strip() if snippet_tag else ""

            results.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })
        return results

    async def _fetch_images(self, context, query: str, count: int) -> List[str]:
        page = await context.new_page()
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/images/search?q={encoded_query}"
        
        image_links = []
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # Wait a bit for JS to load images
            await page.wait_for_timeout(1000) 
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Bing Images are usually in 'a.iusc' with metadata in 'm' attribute
            images = soup.select('a.iusc')[:count]
            import json
            for img in images:
                try:
                    m = img.get('m')
                    if m:
                        meta = json.loads(m)
                        if 'murl' in meta:
                            image_links.append(meta['murl'])
                except:
                    continue
        except Exception as e:
            print(f"Bing image search failed: {e}")
        finally:
            await page.close()
            
        return image_links

    async def _fetch_files(self, context, query: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Your custom logic to find specific file types.
        """
        files_found = {}
        
        # We run these sequentially to avoid triggering bot detection by opening 8 tabs at once
        for filetype in self.file_types:
            page = await context.new_page()
            file_query = f"{query} filetype:{filetype}"
            url = f"{self.base_url}/search?q={urllib.parse.quote(file_query)}"
            
            try:
                await page.goto(url, timeout=20000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                links = []
                for result in soup.find_all("li", class_="b_algo"):
                    h2 = result.find("h2")
                    if not h2: continue
                    a = h2.find("a")
                    if not a: continue
                    
                    file_url = a.get("href")
                    title = a.get_text().strip()
                    
                    if file_url and (f".{filetype}" in file_url.lower()):
                        links.append({"title": title, "url": file_url})
                
                if links:
                    files_found[filetype] = links
            except Exception:
                pass
            finally:
                await page.close()
                
        return files_found

    async def close(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def __aenter__(self):
        await self._ensure_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()