import asyncio
from search_wrapper import BingSearch

async def main():
    print("--- Testing Bing (Playwright) ---")
    
    # We use headless=False so you can SEE the browser working (cool for debugging)
    async with BingSearch(headless=False) as bing:
        results = await bing.search("machine learning pdf", total_search_result=5, total_image_results=3)
        
        print(f"\nFound {len(results['data'])} organic results.")
        print(f"Found {len(results['images'])} images.")
        
        if results.get('files'):
            print("\nFound Files:")
            for ftype, files in results['files'].items():
                print(f"[{ftype}]: {len(files)} files found.")
                print(f" - Example: {files[0]['url']}")

if __name__ == "__main__":
    asyncio.run(main())