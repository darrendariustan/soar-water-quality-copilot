## CV Module (Member 2)

Computer vision for test strip reading and water sample classification. See [docs/cv_module.md](docs/cv_module.md) for setup, usage, and JSON output formats.

### Proposed Scaffolding

```text
water-for-all/
├── .env.example                # Blueprint for system keys (AWS, EXA, OPENAI/BEDROCK)
├── .gitignore                  # Strict filters blocking environment secrets, caches, and logs
├── agents.md                   # Master file defining the 9-agent orchestration system
├── README.md                   # Minimal deployment guides and core architectural summary
├── docs/
│   ├── plan.md                 # Technical execution roadmap with phase-by-phase success criteria
│   └── schema.json             # DB structures (Knowledge, Safety Rules, Results, Risk Tables)
├── infra/                      # Infrastructure as Code (AWS CDK, Terraform, or CloudFormation)
│   ├── aws_stack.tf            # Provisions S3, RDS PostgreSQL, OpenSearch, and API Gateway
│   └── docker/
│       ├── backend.Dockerfile  # Multi-stage production container utilizing uv package manager
│       └── frontend.Dockerfile # Standardized deployment engine for the dashboard app
├── frontend/                   # Web / Mobile user interface (Next.js or React Native)
│   ├── package.json            # Client dependencies and build scripts
│   └── src/                    # UI elements for image uploads and the community risk view
└── backend/                    # Core Python multi-agent logic and analytics engine
    ├── pyproject.toml          # Package spec handled via uv (boto3, opensearch-py, exa-py, pillow)
    ├── uv.lock                 # Deterministic dependency tree locking execution layers
    ├── data/                   # Reference engineering matrices and local mock parameters
    │   ├── raw/                # Baseline test strip images and calibration cards
    │   └── processed/          # Cleaned training sets or local transient configurations
    └── src/
        ├── main.py             # FastAPI entrypoint mapping routes to AWS API Gateway targets
        ├── agents/             # The 9 specified operational multi-agent blueprints
        │   ├── master_agent.py          # Central orchestrator handling final user responses
        │   ├── cv_agent.py              # Vision engine processing strips and clarity
        │   ├── interpretation_agent.py  # Classifies parameters into safety threat tiers
        │   ├── aws_retrieval_agent.py   # Runs semantic vector search queries on OpenSearch
        │   ├── exa_crawl_agent.py       # Dispatches live web crawl alerts for missing data
        │   ├── treatment_agent.py       # Formulates purification / boiling action items
        │   ├── reporting_agent.py       # Analyzes regional trends and aggregates hotspots
        │   ├── education_agent.py       # Translates complex chemistry into clear guidelines
        │   └── safety_agent.py          # Hard gate blocking toxic advice (e.g., boiling chemical contamination)
        ├── tools/              # Discrete infrastructure instruments executed by agents
        │   ├── s3_client.py             # Manages file streaming for image snapshots
        │   ├── rds_client.py            # Executes relational SQL queries against PostgreSQL
        │   ├── opensearch_client.py     # Converts text to embeddings and performs RAG lookup
        │   ├── cv_engine.py             # Evaluates RGB test strip color-matching vectors
        │   └── exa_search.py            # Interfaces with the Exa Search and Retrieval API
        └── pipelines/          # Asynchronous data processing jobs
            ├── ingest_knowledge.py      # Extract, deduplicate, filter, and tag crawled sources
            └── aggregate_analytics.py   # Processes regional failures for local NGO reports
```

---

## Technical Architecture

The WaterForAll system is built upon a six-tier architecture that integrates edge telemetry, multi-agent coordination, and cloud storage:

### Frontend Web / Mobile App
- Upload water image
- Upload test kit image
- Show results and advice
- Show community risk dashboard

### Backend API
- Receives image and user input
- Calls computer vision model
- Calls master agent
- Stores results in AWS

### Computer Vision Layer
- Test strip colour detection
- Reference chart comparison
- Water clarity detection
- Image quality confidence score

### Agentic AI Layer
- Master Water Safety Agent
- Water Quality Agent
- Treatment Guidance Agent
- AWS Knowledge Retrieval Agent
- Exa Web Crawl Agent
- Community Reporting Agent

### Knowledge Layer
- Exa crawls trusted web sources
- Raw content stored in Amazon S3
- Structured knowledge stored in Amazon RDS PostgreSQL
- Embeddings stored in Amazon OpenSearch
- Safety rules stored in database tables

### Analytics Layer
- Community-level unsafe water trends
- Repeated parameter failures
- Location-based risk hotspots
- Reports for NGOs or local agencies

---

## Exa and AWS Knowledge Layer

A key part of WaterForAll is the safe drinking water knowledge base.

We will use Exa to crawl and retrieve trusted web content related to safe drinking water, household water treatment, emergency water safety, boiling guidance, filtration methods, test kit interpretation, chemical contamination warnings, and safe water storage. The crawler should prioritise authoritative sources such as WHO, CDC, UNICEF, government water agencies, public health departments, NGOs, and recognised humanitarian organisations.

The crawled content will not be used blindly. It will go through a knowledge ingestion pipeline before being stored in AWS.

```mermaid
graph TD
    A[Trusted Public Sources] --> B[Exa Web Crawl / Search API]
    B --> C[Content Extraction]
    C --> D[Source Filtering and Deduplication]
    D --> E[Safety Review and Metadata Tagging]
    E --> F[AWS Database Storage]
    F --> G[Embedding and Semantic Search]
    G --> H[RAG Response by WaterForAll Agent]
```

The AWS database will act as the system’s source of truth for safe-drinking-water knowledge and user records.

For the MVP, the AWS architecture can be:

### Amazon S3
Stores raw crawled documents, images, test kit photos and source snapshots.

### Amazon RDS PostgreSQL
Stores structured knowledge, rules, source metadata, user test results, locations, risk levels and audit logs.

### Amazon OpenSearch Service
Stores vector embeddings for semantic search and RAG retrieval.

### AWS Lambda or ECS
Runs ingestion jobs, Exa crawl jobs, data cleaning and agent backend logic.

### Amazon API Gateway
Exposes backend APIs to the frontend app.

### Amazon Bedrock or external LLM API
Generates user-friendly explanations using retrieved knowledge.

---

### Database Schema Design

The database should store both structured and unstructured knowledge.

#### Knowledge table:
- source title
- source URL
- organisation name
- country or region
- topic category
- content summary
- full extracted text
- last crawled date
- safety confidence score
- approved / pending / rejected status

#### Water safety rule table:
- condition
- risk level
- recommended action
- warning message
- source reference
- human review status

#### User test result table:
- anonymised user ID
- test kit type
- parameter readings
- image confidence score
- water appearance classification
- recommended action
- timestamp
- approximate location, if user consents

#### Community risk table:
- area
- repeated unsafe readings
- common parameter failures
- trend over time
- escalation recommendation

This allows the master agent to give advice that is not just based on the LLM’s general knowledge, but based on retrieved, cited, curated and stored public health knowledge.

---

## Updated Agent Architecture

The system will be designed as a master water safety agent supported by specialised sub-agents.

```mermaid
graph TD
    A[User takes photo of water and testing kit] --> B[Computer Vision Agent reads water image and test strip]
    B --> C[Master Agent receives readings and user context]
    C --> D[Water Quality Interpretation Agent checks parameter risks]
    D --> E[AWS Knowledge Retrieval Agent searches stored knowledge]
    E --> F[Exa Web Crawl Agent refreshes missing or outdated guidance]
    F --> G[Treatment Guidance Agent recommends practical actions]
    G --> H[Community Reporting Agent stores anonymised results]
    H --> I[User receives clear, simple and safe advice]
```

The full set of agents includes:

### 1. Master Water Safety Agent
Coordinates all agents and produces the final user-friendly recommendation.

### 2. Computer Vision Agent
Reads the water test kit, detects water appearance, checks image quality and estimates confidence.

### 3. Water Quality Interpretation Agent
Maps test kit readings to simple categories such as safe, caution, unsafe or requires laboratory testing.

### 4. AWS Knowledge Retrieval Agent
Searches the stored safe drinking water knowledge base in Amazon RDS and OpenSearch.

### 5. Exa Web Crawl Agent
Searches and crawls trusted public sources when the database does not have enough information or when guidance needs updating.

### 6. Treatment Guidance Agent
Suggests practical next steps such as settling, filtering, boiling, safe storage, or avoiding the water.

### 7. Community Reporting Agent
Stores anonymised results and identifies repeated unsafe readings in the same area.

### 8. Education Agent
Explains water safety concepts in simple language.

### 9. Safety and Compliance Agent
Prevents the system from giving unsafe advice, such as saying chemically contaminated water is safe after boiling.
