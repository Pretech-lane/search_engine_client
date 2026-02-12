import asyncio
from search_wrapper import GoogleSearchFromSerper, DuckDuckGoSearch

async def main():
    print("--- Testing DuckDuckGo ---")
    async with DuckDuckGoSearch() as ddg:
        results = await ddg.search("python programming", total_search_result=3)
        
        for item in results['data']:
            print(f"\nTitle: {item['title']}")
            print(f"Link:  {item['link']}")
            print(f"Image: {item['image_url']}")

if __name__ == "__main__":
    asyncio.run(main())