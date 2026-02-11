import asyncio
import os
from dotenv import load_dotenv  # Import this
from search_wrapper import GoogleSearchFromSerper


load_dotenv()

async def main():
    # It will now find the key automatically!
    async with GoogleSearchFromSerper() as searcher:
        results = await searcher.search("windows environment variables python")
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
