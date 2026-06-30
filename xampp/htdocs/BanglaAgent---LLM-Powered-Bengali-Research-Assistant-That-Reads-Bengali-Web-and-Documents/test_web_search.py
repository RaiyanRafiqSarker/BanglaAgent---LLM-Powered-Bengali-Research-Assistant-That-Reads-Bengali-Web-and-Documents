"""Quick smoke test for Bengali web search."""
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

sys.path.insert(0, ".")
from src.tools.web_search import search_bengali_web

query = "বাংলাদেশ বাজেট Prothom Alo Daily Star"
print(f"\nSearching: {query}\n")

results = search_bengali_web(query, max_results=5)
print(f"RESULT COUNT: {len(results)}\n")

for i, r in enumerate(results, 1):
    print(f"--- Result {i} ---")
    print(f"  Title:    {r.get('title', 'N/A')}")
    print(f"  URL:      {r.get('url', 'N/A')}")
    print(f"  Source:   {r.get('source_name', 'N/A')}")
    print(f"  Citation: {r.get('citation', 'N/A')}")
    text = r.get("text", "")
    print(f"  Text:     {text[:150]}..." if len(text) > 150 else f"  Text:     {text}")
    print()

if results:
    print("SUCCESS: Web search is working.")
else:
    print("WARNING: No results returned. Check network/DDGS installation.")
