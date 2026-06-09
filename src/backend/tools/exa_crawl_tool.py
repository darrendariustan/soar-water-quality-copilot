"""
Exa web crawl tool. Searches trusted public sources for drinking-water safety
guidance using the Exa API. Configured by EXA_API_KEY.

When the key is absent or the API errors, the tool returns an empty result with
a note instead of raising, so the graph degrades gracefully without fabricating
data.
"""
import os

TRUSTED_DOMAINS = [
    "who.int",
    "cdc.gov",
    "unicef.org",
    "epa.gov",
    "europa.eu",
    "canada.ca",
]


def search_trusted(query: str, num_results: int = 5) -> dict:
    """
    Returns {"used_live": bool, "sources": [{title, url, summary}], "note": str}.
    """
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        return {
            "used_live": False,
            "sources": [],
            "note": "EXA_API_KEY not set; skipped live web crawl.",
        }

    try:
        from exa_py import Exa

        exa = Exa(api_key)
        response = exa.search_and_contents(
            query,
            num_results=num_results,
            include_domains=TRUSTED_DOMAINS,
            type="auto",
            highlights=True,
        )
        sources = []
        for r in response.results:
            summary = ""
            if getattr(r, "highlights", None):
                summary = " ".join(r.highlights)[:400]
            sources.append({"title": r.title or r.url, "url": r.url, "summary": summary})
        return {"used_live": True, "sources": sources, "note": ""}
    except Exception as exc:  # noqa: BLE001
        return {
            "used_live": False,
            "sources": [],
            "note": f"Exa crawl failed: {exc}",
        }
