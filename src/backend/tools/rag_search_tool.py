"""
Knowledge retrieval tool.

Retrieves stored water-safety guidance for a contamination type from the PostgreSQL
knowledge base using pgvector semantic similarity search. This replaces the hardcoded
JSON loader and is ready for production AWS OpenSearch or RDS deployments.
"""
import os
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

def retrieve_guidance(contamination_type: str) -> dict:
    """
    Returns stored guidance for the contamination type using semantic search.

    {"title", "summary", "steps", "sources", "sufficient"}
    sufficient is False when we fall back to the generic 'safe' entry for a
    non-safe contamination type, which signals the master agent that an Exa
    web crawl may add value.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to empty if DB is not configured
        return {
            "title": "Error: Database not configured",
            "summary": "Cannot retrieve guidance because DATABASE_URL is missing.",
            "steps": [],
            "sources": [],
            "sufficient": False,
        }

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://")
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    
    db_url = db_url.replace("@db:", "@localhost:")
    
    # Append short connect_timeout to prevent hanging if DB is unresponsive
    if "?" in db_url:
        db_url += "&connect_timeout=3"
    else:
        db_url += "?connect_timeout=3"

    try:
        embeddings = OpenAIEmbeddings()
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name="water_knowledge",
            connection=db_url,
            use_jsonb=True,
        )

        # Perform similarity search without metadata filter initially to avoid dialect syntax issues
        query = "safe water drinking parameters" if contamination_type == "none" else f"{contamination_type} contamination drinking water safety"
        docs = vector_store.similarity_search(query, k=5)

        if not docs:
            return {
                "title": "No guidance found",
                "summary": "No guidance could be found in the database.",
                "steps": [],
                "sources": [],
                "sufficient": False,
            }

        # Find the matching document locally
        doc = docs[0]  # Fallback to highest similarity
        matched = False
        for d in docs:
            retrieved_type = d.metadata.get("contamination_type", "")
            if retrieved_type == contamination_type or (contamination_type == "none" and retrieved_type == "none"):
                doc = d
                matched = True
                break

        meta = doc.metadata

        meta_sources = meta.get("sources", [])
        formatted_sources = []
        for s in meta_sources:
            if isinstance(s, dict):
                formatted_sources.append(f"{s.get('organisation', 'Unknown')}: {s.get('title', 'Unknown')}")
            else:
                formatted_sources.append(str(s))

        return {
            "title": meta.get("title", "Unknown Title"),
            "summary": meta.get("summary", "No summary available."),
            "steps": meta.get("steps", []),
            "sources": formatted_sources,
            "sufficient": matched,
        }
    except Exception as exc:
        return {
            "title": "Database Error",
            "summary": f"Failed to retrieve from pgvector: {exc}",
            "steps": [],
            "sources": [],
            "sufficient": False,
        }
