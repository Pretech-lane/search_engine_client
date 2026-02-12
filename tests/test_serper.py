import asyncio
from dotenv import load_dotenv
# We import from the FOLDER name, which works because of __init__.py
from search_wrapper import GoogleSearchFromSerper 

load_dotenv()

async def main():
    # Make sure your .env file has GOOGLE_SERPER_API_KEY=...
    async with GoogleSearchFromSerper() as searcher:
        print("Searching...")
        results = await searcher.search("windows environment variables python")
        
        # Print results clearly
        if results.get('data'):
            print(f"Found {len(results['data'])} text results.")
            print("First result title:", results['data'][0].get('title'))
        else:
            print("No text results found.")

if __name__ == "__main__":
    asyncio.run(main())