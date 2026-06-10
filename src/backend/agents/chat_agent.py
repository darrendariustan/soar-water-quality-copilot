"""
Agentic UI Chat Assistant loop.
Equipped with conversation memory and tools (RAG, Exa, AWS DB).
"""
import json
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from agents.llm import get_llm
from tools.rag_search_tool import retrieve_guidance
from tools.exa_crawl_tool import search_trusted
from tools.aws_db_tool import get_community_risk

@tool
def search_local_guidance(contamination_type: str) -> dict:
    """Search the local safe drinking water knowledge base for guidance on specific parameters or contaminations."""
    return retrieve_guidance(contamination_type)

@tool
def search_web_trusted(query: str) -> dict:
    """Search the web across trusted public sources (WHO, CDC, etc.) for water safety guidance."""
    return search_trusted(query)

@tool
def check_community_risk(area: str) -> dict:
    """Check the database for community risk trends in a specific area to see if others reported issues."""
    return get_community_risk(area)

def get_chat_agent(system_prompt: str):
    llm = get_llm(temperature=0.3, streaming=True)
    tools = [search_local_guidance, search_web_trusted, check_community_risk]
    agent_executor = create_react_agent(llm, tools=tools, prompt=system_prompt)
    return agent_executor
