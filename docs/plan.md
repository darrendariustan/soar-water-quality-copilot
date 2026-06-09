# High Level Steps for Project

Part 1: Plan and Scaffolding Verification

[ ] Verify root directory layout and confirm [agents.md](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/agents.md) is correctly placed within the project root directory.
[ ] Create directory structure under the root:
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
[ ] Establish validation checks for mock water test and appearance image metadata payloads.

- Judging Criteria Alignment: Maps to Agent Overview by validating the core identity, layout, and purpose of the WaterForAll Assistant before coding.
- Success Criteria: Execution architecture verification and workspace scaffolding setup.
- Tests: Structural file existence check for agents, tools, and app.

Part 2: Docker Infrastructure and Environment Setup

[ ] Write a `docker-compose.yml` and root-level `Dockerfile` utilizing multi-stage builds and `uv` to install FastAPI/LangGraph dependencies.
[ ] Configure a local robust PostgreSQL container within `docker-compose.yml` to simulate Amazon RDS.
[ ] Configure `.env` mapping for environmental secrets management (`OPENAI_API_KEY`, `EXA_API_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
[ ] Write localized execution scripts (`start-server.sh`, `start-server.bat`, `stop-server.sh`, and `stop-server.bat`) inside `scripts/`.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Failure Handling by setting up the closed, cross-platform container sandbox environment that isolates OS-specific engineering dependencies.
- Success Criteria: Docker images compile cleanly; container runs a baseline Next.js application page and FastAPI backend accessible at localhost, with PostgreSQL running.
- Tests: Execute container ping tests for frontend, backend, and database; verify `uv` lockfile generation integrity.

Part 3: Static Asset Integration and Caching

[ ] Configure AWS SDK (Boto3) to connect to Amazon Rekognition for computer vision inference.
[ ] Implement API wrapper logic for submitting water sample images and receiving parameter classifications from Rekognition.

- Judging Criteria Alignment: Maps to Actions & Tool Use by binding backend classification and computer vision tools as cloud execution helpers.
- Success Criteria: App boots instantly and successfully communicates with Amazon Rekognition API.
- Tests: Assert AWS credentials load successfully; verify the image processing parser receives valid JSON from Rekognition.

Part 4: WaterForAll Dashboard Layout

[ ] Implement a decoupled Next.js + React frontend with Tailwind CSS (in `src/frontend/`) mapped to a sleek dark utility UI theme with Water Blue Primary (`#209dd7`).
[ ] Define the layout with three main sections:
    1. Water Image & Test Strip Upload Section: Interface to upload water appearance photos and test strip results.
    2. Safety Diagnosis & Advice Panel: Displays classification readings, confidence, safety risk level (Safe, Caution, Unsafe), and treatment recommendations.
    3. Community Risk Dashboard: Visualizes repeated unsafe readings, common parameter failures, trends over time, and location hotspots.
[ ] Add a sidebar for the multi-agent conversational chat interface.

- Judging Criteria Alignment: Maps to Demo & Presentation by structuring a high-fidelity, scannable corporate utility dashboard.
- Success Criteria: Clean, responsive rendering of image upload controls, parameters, and interactive charts on canvas loading.
- Tests: Verification of visual element DOM mounting via tests.

Part 5: Decoupled Multi-Agent and Database/Tool Implementation

[ ] Implement isolated tools inside `src/tools/`:
    - `cv_tool.py`: Wraps Amazon Rekognition API calls for analysis of test strip colors and water clarity.
    - `aws_db_tool.py`: Integrates with the local Docker PostgreSQL container to mock Amazon RDS structured tables (Knowledge, Rule, User Test Result, Community Risk).
    - `rag_search_tool.py`: Performs vector search or semantic matching against knowledge tables.
    - `exa_crawl_tool.py`: Performs targeted search/crawls against the Exa API for trusted sources.
[ ] Implement specialized, autonomous agents inside `src/agents/` driven by **LangGraph** for orchestration:
    - `master_agent.py`: The LangGraph supervisor that coordinates the agents, aggregates parameters, and compiles final recommendations.
    - `cv_agent.py`: LangGraph node to read the water test kit and clarity via `cv_tool.py`.
    - `water_quality_agent.py`: Maps parameter readings (pH, chlorine, turbidity, nitrate, nitrite, hardness, iron) to risk categories.
    - `aws_retrieval_agent.py`: Queries AWS OpenSearch/RDS PostgreSQL tables for water safety rules and guides.
    - `exa_crawl_agent.py`: Invokes the Exa crawl tool to search trusted public sources (WHO, CDC, etc.) for missing/outdated rules.
    - `treatment_guidance_agent.py`: Determines practical household water treatment actions (settling, filtering, boiling, safe storage).
    - `community_reporting_agent.py`: Stores anonymized results and updates local area trends.
    - `education_agent.py`: Explains concepts in simple terms.
    - `safety_agent.py`: Inspects advice to prevent hazardous guidelines (e.g. advising boiling for chemical contaminants).
[ ] Implement compute automation pipelines inside `src/pipelines/`:
    - `ingest_knowledge.py`: Ingests and embeds crawling results into PostgreSQL.

- Judging Criteria Alignment: Maps to Agent Overview, Autonomy & Decision-Making, Actions & Tool Use, and Compute Automation Boundaries by building decoupled agents, isolated tools, and execution pipelines.
- Success Criteria: Specialist agents successfully interact with tools and pipelines, communicating with the Master Agent using structured JSON control payloads.
- Tests: Deterministic unit tests confirming individual agents and pipelines process data payloads and output expected structures.

Part 6: Injected Parameter Scenario Controls and Orchestration Flow

[ ] Create UI controls (scenario triggers/dropdowns) in the app to trigger pre-configured "Water Quality Scenarios" (e.g., Safe Water, Microbiological Outbreak, Chemical Contamination) to contrast normal operations against anomalies.
[ ] Implement the orchestration flow upon scenario trigger:
    1. UI scenario trigger or image upload -> `master_agent.py`.
    2. `master_agent.py` invokes `cv_agent.py` (via `cv_tool.py`) to extract parameters.
    3. `master_agent.py` delegates to `water_quality_agent.py` to identify risks.
    4. `master_agent.py` coordinates with `aws_retrieval_agent.py` to fetch stored safety guides.
    5. If details are missing, `master_agent.py` activates `exa_crawl_agent.py` to query Exa API.
    6. `master_agent.py` executes `treatment_guidance_agent.py` and `safety_agent.py` to produce safety warnings/guidelines.
    7. `master_agent.py` commands `community_reporting_agent.py` to store anonymized analytics data.
[ ] Update the dashboard elements dynamically on alert triggers, shifting the theme from safe primary blue/green to warning/danger (orange/red).

- Judging Criteria Alignment: Maps to Human-in-the-Loop, Orchestration, and Story Arc Alignment by allowing the presenter/operator to force anomalies and observe the live multi-agent reaction.
- Success Criteria: Toggling the demo switch shifts the interface state smoothly from a standard profile to a warning/danger view with updated explanation panels and retrieval data.
- Tests: Verify session state mutations and that the end-to-end data pipeline completes successfully without UI freezing.

Part 7: Exa API Integration via Web Crawl Agent

[ ] Integrate `exa_crawl_tool.py` with the external Exa API, routing requests securely using the `EXA_API_KEY`.
[ ] Construct targeted search queries matching coordinates/country, contaminant parameters, and trusted domains (e.g., who.int, cdc.gov).
[ ] Render the structured context headlines and summaries within the retrieval context dashboard component.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Autonomy & Decision-Making by empowering the RAG tool to fetch real-world context for anomalous parameter coordinates.
- Success Criteria: Web query results return clean, structured real-time context relevant to the parameter and region.
- Tests: Mock API integration testing ensuring graceful handling of network timeouts or empty search results payloads.

Part 8: External LLM Client Integration and Exception Handling

[ ] Configure the LLM API client framework (Bedrock/OpenAI) using the secure environment variables to drive agent reasoning.
[ ] Implement localized emergency failure handling: If external endpoints (LLM or Exa) timeout or fail, the Master Agent catches the exception, activates a localized emergency state, maps the frontend to pure local rules/CV algorithms, and flashes a warning banner.

- Judging Criteria Alignment: Maps to Failure Handling and Orchestration by establishing fallback pathways for external services.
- Success Criteria: API exceptions do not crash the app, but instead trigger a clean downgrade to local-only diagnostics.
- Tests: Force connection timeouts or use invalid credentials and verify that the dashboard switches to emergency fallback mode with a warning banner.

Part 9: Prompt Engineering and Hub-and-Spoke Orchestration

[ ] Define the structured JSON schemas passed exclusively between the specialized agents and the central Master Agent (avoiding global broadcasts).
[ ] Program prompt templates for each agent in `src/agents/` that define their roles, enforce the localized Plan-Execute-Reflect reasoning, and prevent defensive filler text.
[ ] Implement the asynchronous communication flow routing all specialist payloads strictly through the central Master Agent.

- Judging Criteria Alignment: Maps to Orchestration and Autonomy & Decision-Making by establishing a clean Hub-and-Spoke communication layer.
- Success Criteria: Master Agent coordinates CV, water quality, and treatment guidance outputs purely using structured JSON payloads.
- Tests: Validate that structured JSON output schemas match input constraints for each agent.

Part 10: Streaming UI Sidebar & Human-in-the-Loop Integration

[ ] Implement a collapsible conversational chat sidebar in the application layout.
[ ] Use streaming responses to stream the Education Agent's explanations and responses.
[ ] Implement operator review controls: allow the operator to override automated decisions, adjust parameter levels manually, and approve/veto community hazard alerts before logging them to the AWS tables.
[ ] Implement CV tool divergence/failure handling: If the computer vision module fails to detect colors due to poor lighting, catch the exception and fall back to manual parameter inputs with an alert banner.

- Judging Criteria Alignment: Maps to Human-in-the-Loop, Failure Handling, and Demo & Presentation by providing interactive control features, streaming outputs, and solver robustness.
- Success Criteria: Smooth, token-by-token sidebar text streaming and operational override controls without UI blocking or crashes.
- Tests: Run integration tests to confirm the app boots, executes scenarios, updates database records, handles CV/API failures, and streams conversational text without runtime failures.