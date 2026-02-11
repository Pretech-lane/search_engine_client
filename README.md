# Search Engine Client

Lightweight, async wrappers around multiple search engine APIs (Serper/Google, DuckDuckGo, Bing). This package provides a small, opinionated interface for running text and image searches and returning standardized results.

## Features

- Async-first search engine clients implementing a common `BaseSearchEngine` interface.
- Built-in engines: Serper (Google), DuckDuckGo, Bing (concrete implementations in `src/search_wrapper/engines`).
- Concurrent text + image fetching for engines that support both.

## Installation

Install for development (editable) and add required dependencies:

```bash
pip install -e .
pip install httpx
```

## Quick start

Set the required API key for services that need one (example for Serper/Google):

```powershell
$env:GOOGLE_SERPER_API_KEY = "your_api_key_here"
```

Example usage (async):

```python
import asyncio
from search_wrapper import GoogleSearchFromSerper

async def main():
	async with GoogleSearchFromSerper(api_key="YOUR_KEY") as client:
		results = await client.search("python async http client")
		print(results)

asyncio.run(main())
```

Alternatively import specific engine directly:

```python
from search_wrapper.engines.serper import GoogleSearchFromSerper
```

## Development notes

- Source layout lives under `src/` (package name: `search_wrapper`). Either install the package in editable mode (`pip install -e .`) or add `src` to `PYTHONPATH`/VS Code `python.analysis.extraPaths` so imports resolve in the editor.
- The Serper client uses `httpx.AsyncClient` — ensure `httpx` is installed in your active environment.
- Tests and examples live at the project root (`test_search.py`, `main.py`).

## Contributing

Feel free to open issues or PRs. When adding new engines, implement `BaseSearchEngine` and expose the engine in `src/search_wrapper/__init__.py`.

---
