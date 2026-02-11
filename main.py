# import asyncio
# from dotenv import load_dotenv
# # We import from the FOLDER name, which works because of __init__.py
# from search_wrapper import GoogleSearchFromSerper 

# load_dotenv()

# async def main():
#     # Make sure your .env file has GOOGLE_SERPER_API_KEY=...
#     async with GoogleSearchFromSerper() as searcher:
#         print("Searching...")
#         results = await searcher.search("windows environment variables python")
        
#         # Print results clearly
#         if results.get('data'):
#             print(f"Found {len(results['data'])} text results.")
#             print("First result title:", results['data'][0].get('title'))
#         else:
#             print("No text results found.")

# if __name__ == "__main__":
#     asyncio.run(main())


###DuckDuckgo testing


# import asyncio
# from search_wrapper import GoogleSearchFromSerper, DuckDuckGoSearch

# async def main():
#     print("--- Testing DuckDuckGo ---")
#     async with DuckDuckGoSearch() as ddg:
#         results = await ddg.search("python programming", total_search_result=3)
        
#         for item in results['data']:
#             print(f"\nTitle: {item['title']}")
#             print(f"Link:  {item['link']}")
#             print(f"Image: {item['image_url']}")

# if __name__ == "__main__":
#     asyncio.run(main())



#bing testing

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