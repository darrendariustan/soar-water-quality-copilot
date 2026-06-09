import os
import json
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document

def ingest_all():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set. Skipping ingestion.")
        return

    # Fix the DB URL dialect if necessary for psycopg
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://")
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    
    db_url = db_url.replace("@db:", "@localhost:")

    # Initialize the PGVector store
    embeddings = OpenAIEmbeddings()
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="water_knowledge",
        connection=db_url,
        use_jsonb=True,
    )

    base_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge")
    guidance_path = os.path.join(base_dir, "guidance.json")
    sources_path = os.path.join(base_dir, "sources.json")

    with open(guidance_path, "r", encoding="utf-8") as f:
        guidance = json.load(f)
    
    with open(sources_path, "r", encoding="utf-8") as f:
        sources_dict = json.load(f)

    docs = []
    for key, data in guidance.items():
        # Combine the title, summary, and steps as the searchable content
        content = f"{data['title']}\n{data['summary']}\n" + "\n".join(data['steps'])
        
        # Look up full source objects
        sources = []
        for sid in data.get("source_ids", []):
            if sid in sources_dict:
                sources.append(sources_dict[sid])

        metadata = {
            "contamination_type": data.get("contamination_type", key),
            "title": data["title"],
            "summary": data["summary"],
            "steps": data["steps"],
            "sources": sources,
        }
        
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)

    print(f"Ingesting {len(docs)} documents into PGVector...")
    vector_store.add_documents(docs)
    print("Ingestion complete!")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest_all()
