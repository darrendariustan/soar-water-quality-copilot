"""
AWS Knowledge Retrieval Agent.

Retrieves stored water-safety guidance for the assessed contamination type
through the knowledge retrieval tool (cited knowledge base now, pgvector/RDS
later). Sets a sufficiency flag the master agent uses to decide whether to
trigger the Exa web crawl.
"""
from tools.rag_search_tool import retrieve_guidance
from agents.schemas import KnowledgeResult
from agents.state import GraphState


def aws_retrieval_agent(state: GraphState) -> dict:
    contamination = state["quality"].contamination_type
    found = retrieve_guidance(contamination)

    knowledge = KnowledgeResult(
        title=found["title"],
        summary=found["summary"],
        steps=found["steps"],
        sources=found["sources"],
        sufficient=found["sufficient"],
    )
    return {"knowledge": knowledge}
