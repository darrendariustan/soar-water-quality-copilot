# High Level Steps for Project

Part 1: Plan and Scaffolding Verification

[x] Verify root directory layout and confirm [agents.md](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/agents.md) is correctly placed within the project root directory.

[x] Create directory structure under the root:
    - `src/`
    - `src/agents/`
    - `src/tools/`
    - `src/pipelines/`
    - `models/`
    - `data/`
    - `data/raw/`
    - `data/processed/`
    - `notebooks/`
    - `scripts/`
    - `docs/`
[x] Establish validation checks for mock water test and appearance image metadata payloads.

- Judging Criteria Alignment: Maps to Agent Overview by validating the core identity, layout, and purpose of the WaterForAll Assistant before coding.
- Success Criteria: Execution architecture verification and workspace scaffolding setup.
- Tests: Structural file existence check for agents, tools, and app.

Part 2: Docker Infrastructure and Environment Setup

[x] Write a `docker-compose.yml` and root-level `Dockerfile` utilizing multi-stage builds and `uv` to install FastAPI/LangGraph dependencies.

[x] Configure a local robust PostgreSQL container within `docker-compose.yml` to simulate Amazon RDS.

[x] Configure `.env` mapping for environmental secrets management (`OPENAI_API_KEY`, `EXA_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

[x] Write localized execution scripts (`start-server.sh`, `start-server.bat`, `stop-server.sh`, and `stop-server.bat`) inside `scripts/`.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Failure Handling by setting up the closed, cross-platform container sandbox environment that isolates OS-specific engineering dependencies.
- Success Criteria: Docker images compile cleanly; container runs a baseline Next.js application page and FastAPI backend accessible at localhost, with PostgreSQL running.
- Tests: Execute container ping tests for frontend, backend, and database; verify `uv` lockfile generation integrity.

Part 3: Static Asset Integration and Caching

[x] Configure AWS SDK (Boto3) to connect to Amazon Rekognition for computer vision inference.

[x] Implement API wrapper logic for submitting water sample images and receiving parameter classifications from Rekognition.

- Judging Criteria Alignment: Maps to Actions & Tool Use by binding backend classification and computer vision tools as cloud execution helpers.
- Success Criteria: App boots instantly and successfully communicates with Amazon Rekognition API.
- Tests: Assert AWS credentials load successfully; verify the image processing parser receives valid JSON from Rekognition.

Part 4: WaterForAll Dashboard Layout

[x] Implement a decoupled Next.js + React frontend with Tailwind CSS (in `src/frontend/`) mapped to a sleek dark utility UI theme with Water Blue Primary (`#209dd7`).

[x] Define the layout with three main sections:
    1. Water Image & Test Strip Upload Section: Interface to upload water appearance photos and test strip results.
    2. Safety Diagnosis & Advice Panel: Displays classification readings, confidence, safety risk level (Safe, Caution, Unsafe), and treatment recommendations.
    3. Community Risk Dashboard: Visualizes repeated unsafe readings, common parameter failures, trends over time, and location hotspots.

[x] Add a sidebar for the multi-agent conversational chat interface.

- Judging Criteria Alignment: Maps to Demo & Presentation by structuring a high-fidelity, scannable corporate utility dashboard.
- Success Criteria: Clean, responsive rendering of image upload controls, parameters, and interactive charts on canvas loading.
- Tests: Verification of visual element DOM mounting via tests against the new `<AppPage />` layout and integrated components.

Part 5: Decoupled Multi-Agent and Database/Tool Implementation

[x] Implement isolated tools inside `src/backend/tools/`:
    - `cv_tool.py`: Wraps Amazon Rekognition API calls for analysis of test strip colors and water clarity.
    - `aws_db_tool.py`: Integrates with the local Docker PostgreSQL container to mock Amazon RDS structured tables (Knowledge, Rule, User Test Result, Community Risk).
    - `rag_search_tool.py`: Performs pgvector semantic similarity search against the PostgreSQL knowledge table using OpenAIEmbeddings.
    - `exa_crawl_tool.py`: Performs targeted search/crawls against the Exa API for trusted sources.

[x] Implement specialized, autonomous agents inside `src/backend/agents/` driven by **LangGraph** for orchestration:
    - `master_agent.py`: The LangGraph supervisor that coordinates the agents, aggregates parameters, and compiles final recommendations.
    - `cv_agent.py`: LangGraph node to read the water test kit and clarity via `cv_tool.py`.
    - `water_quality_agent.py`: Maps parameter readings (pH, chlorine, turbidity, nitrate, nitrite, hardness, iron) to risk categories.
    - `aws_retrieval_agent.py`: Queries PostgreSQL/pgvector tables for water safety rules and guides.
    - `exa_crawl_agent.py`: Invokes the Exa crawl tool to search trusted public sources (WHO, CDC, etc.) for missing/outdated rules.
    - `treatment_guidance_agent.py`: Determines practical household water treatment actions (settling, filtering, boiling, safe storage).
    - `community_reporting_agent.py`: Stores anonymized results and updates local area trends.
    - `education_agent.py`: Explains concepts in simple terms.
    - `safety_agent.py`: Inspects advice to prevent hazardous guidelines (e.g. advising boiling for chemical contaminants).

[x] Implement compute automation pipelines inside `src/backend/pipelines/`:
    - `ingest_knowledge.py`: Parses the local JSON knowledge bases (e.g. `guidance.json`, `sources.json`), embeds them using OpenAIEmbeddings, and ingests them into the pgvector PostgreSQL tables. It will also be capable of embedding raw Exa crawling results into PostgreSQL.

- Judging Criteria Alignment: Maps to Agent Overview, Autonomy & Decision-Making, Actions & Tool Use, and Compute Automation Boundaries by building decoupled agents, isolated tools, and execution pipelines.
- Success Criteria: Specialist agents successfully interact with tools and pipelines, communicating with the Master Agent using structured JSON control payloads.
- Tests: Deterministic unit tests confirming individual agents and pipelines process data payloads and output expected structures.

Part 6: Injected Parameter Scenario Controls and Orchestration Flow

[x] Add manual scenario controls (e.g., draggable sliders for Turbidity, Chlorine, pH, Nitrate) to the Next.js React frontend so the demo can manually inject parameter anomalies without needing a live photo.

[x] Implement the CV submission orchestration flow:
    - Added `POST /api/analyze` to handle multipart physical image uploads which processes bytes via `process_submission` and maps the results into the `master_agent` pipeline.
    - Added `POST /cv/submissions` to handle manual JSON parameter inputs and maps them into the `master_agent` pipeline.
    - Implemented `process_submission()` in `src/backend/cv/submission_handler.py`.

1. User uploads 1-3 images in the UI (or uses manual scenario controls) -> POST `/cv/submissions` (`src/backend/main.py`). 

2. For each image, kit type is taken from the declared kit_types form field or inferred by `kit_classifier.py` (local heuristic or LLM). 

3. Each image is routed to its processor: generic 16-in-1 strip (`engine.py`), heavy metals strip (`heavy_metals_processor.py`), or TDS meter (`tds_processor.py`). In cloud mode these call the LLM API via `aws_provider.py`; in local mode they use OpenCV heuristics. 

4. Per-image ImageResults are aggregated into a single SubmissionResult, including deduplicated `combined_boiling_resistant_risk_flags` (highest severity per parameter). 

5. For the local MVP, the endpoint mocks persistence and directly returns the `SubmissionResult` to the frontend without requiring DynamoDB. 

6. The CV module deliberately stops at readings, confidence scores, and boiling-resistant risk flags; it never declares water safe or unsafe. Final guidance is handed off to the downstream Water Quality and Treatment agents.

[x] Make the results UI react to risk: shift result cards and banners by risk_category and boiling-risk severity - neutral/low readings render in the primary Water Blue (#209dd7), treatment_required/warning shift to amber, and critical/boiling-resistant flags shift to red with a prominent warning banner.

- Judging Criteria Alignment: Maps to Orchestration, Human-in-the-Loop, and Story Arc Alignment by letting the presenter force scenarios and observe the multi-image CV pipeline react end to end.

- Success Criteria: Selecting a scenario or uploading images produces a structured SubmissionResult, persists it (AWS mode), and the dashboard smoothly shifts from a normal profile to a warning/danger view with updated readings and risk flags.

- Tests: tests/cv/test_submission.py already covers process_submission() routing, aggregation, and combined-flag dedup; additionally verify scenario triggers render the correct risk state in the UI without freezing.

Part 7: Exa API Integration via Web Crawl Agent

[x] **Part 7: Exa API Integration via Web Crawl Agent** *(Status: COMPLETE)*

[x] Integrate `exa_crawl_tool.py` with the external Exa API, routing requests securely using the `EXA_API_KEY`.
[x] Construct targeted search queries matching coordinates/country, contaminant parameters, and trusted domains (e.g., who.int, cdc.gov).
[x] Render the structured context headlines and summaries within the retrieval context dashboard component.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Autonomy & Decision-Making by empowering the RAG tool to fetch real-world context for anomalous parameter coordinates.
- Success Criteria: Web query results return clean, structured real-time context relevant to the parameter and region.
- Tests: Mock API integration testing ensuring graceful handling of network timeouts or empty search results payloads.

Part 8: External LLM Client Integration and Exception Handling

[x] Configure the LLM API client framework (OpenAI compatible) using the secure environment variables to drive agent reasoning.

[x] Implement localized emergency failure handling: If external endpoints (LLM or Exa) timeout or fail, the Master Agent catches the exception, activates a localized emergency state, maps the frontend to pure local rules/CV algorithms, and flashes a warning banner.

- Judging Criteria Alignment: Maps to Failure Handling and Orchestration by establishing fallback pathways for external services.
- Success Criteria: API exceptions do not crash the app, but instead trigger a clean downgrade to local-only diagnostics.
- Tests: Force connection timeouts or use invalid credentials and verify that the dashboard switches to emergency fallback mode with a warning banner.

Part 9: Prompt Engineering and Hub-and-Spoke Orchestration

[x] Define the structured JSON schemas passed exclusively between the specialized agents and the central Master Agent (avoiding global broadcasts).

[x] Program prompt templates for each agent in `src/backend/agents/` that define their roles, enforce the localized Plan-Execute-Reflect reasoning, and prevent defensive filler text.

[x] Implement the asynchronous communication flow routing all specialist payloads strictly through the central Master Agent.

- Judging Criteria Alignment: Maps to Orchestration and Autonomy & Decision-Making by establishing a clean Hub-and-Spoke communication layer.
- Success Criteria: Master Agent coordinates CV, water quality, and treatment guidance outputs purely using structured JSON payloads.
- Tests: Validate that structured JSON output schemas match input constraints for each agent.

Part 10: Streaming UI Sidebar & Human-in-the-Loop Integration

[ ] Implement a collapsible conversational chat sidebar in the application layout.

[ ] Use streaming responses to stream the Education Agent's explanations and responses.

[ ] Implement operator review controls: allow the operator to override automated decisions, adjust parameter levels manually, and approve/veto community hazard alerts before logging them to the database tables (local PostgreSQL for MVP, Amazon RDS for production).

[ ] Implement CV tool divergence/failure handling: If the computer vision module fails to detect colors due to poor lighting, catch the exception and fall back to manual parameter inputs with an alert banner.

- Judging Criteria Alignment: Maps to Human-in-the-Loop, Failure Handling, and Demo & Presentation by providing interactive control features, streaming outputs, and solver robustness.
- Success Criteria: Smooth, token-by-token sidebar text streaming and operational override controls without UI blocking or crashes.
- Tests: Run integration tests to confirm the app boots, executes scenarios, updates database records, handles CV/API failures, and streams conversational text without runtime failures.

Part 11: Final Production Deployment

[ ] Package the FastAPI backend and LangGraph agents into a production Docker image and push to Amazon ECR.

[ ] Deploy the backend to AWS Lambda (using Mangum) or Amazon ECS for scalable compute execution.

[ ] Deploy Amazon API Gateway to act as the secure front door routing requests from the Next.js frontend to the backend API.

[ ] Migrate from the local PostgreSQL Docker container to a production Amazon RDS PostgreSQL instance, retaining the use of `pgvector` for semantic search and vector embeddings.

[ ] Update Next.js frontend `.env` to point to the production API Gateway URL and deploy the frontend application.

- Judging Criteria Alignment: Maps to Action & Tool Use and Orchestration by ensuring the multi-agent system runs securely and scalably in the cloud.
- Success Criteria: The web application is accessible via a public URL, handles image uploads, and successfully interacts with the cloud backend through API Gateway.
- Tests: Execute end-to-end integration tests hitting the API Gateway endpoint to verify AWS RDS, S3, and Rekognition functionality.
