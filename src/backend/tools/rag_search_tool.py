"""
Knowledge retrieval tool.

Retrieves stored water-safety guidance for a contamination type from the cited
knowledge base (the seed source of truth). This is the interface the AWS
knowledge retrieval agent calls; a pgvector/OpenSearch semantic backend can be
substituted here later without changing the agent.
"""
from knowledge.loader import lookup_guidance, guidance_sources


def retrieve_guidance(contamination_type: str) -> dict:
    """
    Returns stored guidance for the contamination type.

    {"title", "summary", "steps", "sources", "sufficient"}
    sufficient is False when we fall back to the generic 'safe' entry for a
    non-safe contamination type, which signals the master agent that an Exa
    web crawl may add value.
    """
    entry = lookup_guidance(contamination_type)
    matched = entry.get("contamination_type") == contamination_type or contamination_type == "none"
    return {
        "title": entry["title"],
        "summary": entry["summary"],
        "steps": entry["steps"],
        "sources": guidance_sources(entry),
        "sufficient": matched,
    }
