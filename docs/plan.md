# High Level Steps for Project

Part 1: Plan and Scaffolding Verification

[ ] Verify root directory layout and confirm [agents.md](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/agents.md) is correctly placed within the project root directory.
[ ] Create directory structure under the root:
    - `src/`
    - `src/agents/`
    - `src/tools/`
    - `src/pipelines/`
    - `models/`
    - `data/epanet/`
    - `data/raw/`
    - `data/processed/`
    - `notebooks/`
    - `scripts/`
    - `docs/`
[ ] Establish validation checks for mock data payloads.

- Judging Criteria Alignment: Maps to Agent Overview by validating the core identity, layout, and purpose of the Hydraulic Copilot before coding.
- Success Criteria: Execution architecture verification and workspace scaffolding setup.
- Tests: Structural file existence check for agents, tools, and app.

Part 2: Docker Infrastructure and Environment Setup

[ ] Write a root-level `Dockerfile` utilizing multi-stage builds and `uv` to install dependencies including `torch` and `wntr`.
[ ] Configure `.env` mapping for environmental secrets management (`OPENAI_API_KEY`, `EXA_API_KEY`).
[ ] Write localized execution scripts (`start-server.sh`, `start-server.bat`, `stop-server.sh`, and `stop-server.bat`) inside `scripts/`.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Failure Handling by setting up the closed, cross-platform container sandbox environment that isolates OS-specific engineering dependencies.
- Success Criteria: Docker image compiles cleanly using `uv` package manager; container runs a baseline Streamlit page accessible at localhost:8501.
- Tests: Execute container ping test; verify `uv` lockfile generation integrity.

Part 3: Static Asset Integration and Caching

[ ] Place EPANET network file `network.inp` inside `data/epanet/` and baseline telemetry dataset `water_potability.csv` inside `data/raw/`.
[ ] Place ML checkpoints (`potability_model.pkl` and PyTorch physics-informed neural network weights `weights.pth`) inside `models/`.
[ ] Implement `st.cache_resource` wrapper pipelines in the app to load `network.inp` via WNTR and the ML classification model weights exactly once.

- Judging Criteria Alignment: Maps to Actions & Tool Use by binding the backend simulation and neural network environments as local execution tools.
- Success Criteria: App boots instantly without repeating heavy disk read routines on user window reruns.
- Tests: Assert model checkpoints load successfully; verify WNTR parses network junctions without errors.

Part 4: Geospatial Network Dashboard Layout

[ ] Implement a single-page Streamlit view in [app.py](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/src/app.py) mapped to a sleek dark utility UI theme.
[ ] Define the layout with three main columns:
    1. Geospatial Network Topology Map: Heatmap showing pressure and water-age using Plotly or PyVis.
    2. Anomaly Alert Panel: Detailed display showing leak probabilities, potability indexes, and physics residual scores.
    3. Exa Context Panel: Dedicated section rendering real-time retrieved geospatial context.
[ ] Add a sidebar for the multi-agent conversational chat interface.

- Judging Criteria Alignment: Maps to Demo & Presentation by structuring a high-fidelity, scannable corporate utility dashboard.
- Success Criteria: Clean, responsive rendering of network nodes with scannable labels on canvas loading.
- Tests: Verification of visual element DOM mounting via Streamlit AppTest framework.

Part 5: Decoupled Multi-Agent and Tool Implementation

[ ] Implement isolated tools inside `src/tools/`:
    - `epanet_tool.py`: Wraps WNTR to programmatically interact with and modify `.inp` network topologies on-the-fly.
    - `ml_model_tool.py`: Handles local evaluation checkpoints for classical classification (`potability_model.pkl`) and deep physics-informed structural tensors.
    - `sensor_tool.py`: Manages structural sensor array mappings, downsampling high-density grid fields to sparse telemetry feeds.
    - `rag_tool.py`: Performs targeted geospatial queries against the Exa API for context (road closures, weather, excavation permits).
[ ] Implement specialized, autonomous agents inside `src/agents/` driven by a localized Plan-Execute-Reflect loop:
    - `planner_agent.py`: Central supervisor/router parsing operator queries/UI events and routing tasks using structured JSON.
    - `simulation_agent.py`: Manages physical state calculations, velocity, water age, and mass-balance using the EPANET solver tool.
    - `risk_agent.py`: Evaluates leak probabilities and potability anomalies using the ML model tool.
    - `explanation_agent.py`: Synthesizes technical parameters and RAG context into natural-language briefings for field crews.
[ ] Implement compute automation pipelines inside `src/pipelines/`:
    - `train_potability_model.py`: Offline processing code to build or update model assets.
    - `run_water_quality_scenario.py`: Deterministic end-to-end pipeline simulating anomalies.

- Judging Criteria Alignment: Maps to Agent Overview, Autonomy & Decision-Making, Actions & Tool Use, and Compute Automation Boundaries by building decoupled agents, isolated tools, and execution pipelines.
- Success Criteria: Specialist agents successfully interact with tools and pipelines, communicating with the Planner Agent using structured JSON control payloads.
- Tests: Deterministic unit tests confirming individual agents and pipelines process data payloads and output expected structures.

Part 6: Injected Leak Scenario State Controls and Orchestration Flow

[ ] Create UI controls (scenario triggers) in [app.py](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/src/app.py) to trigger pre-configured "Injected Water Quality & Leak Scenarios" to contrast normal operations against anomalies.
[ ] Implement the orchestration flow upon scenario trigger:
    1. UI scenario trigger -> `planner_agent.py`.
    2. `planner_agent.py` calls `sensor_tool.py` and delegates to `simulation_agent.py` to isolate hydraulic changes.
    3. `simulation_agent.py` processes state via `epanet_tool.py` and returns metrics.
    4. `planner_agent.py` passes metrics to `risk_agent.py`, which calls `ml_model_tool.py` to evaluate potability and leak vectors.
    5. `planner_agent.py` aggregates all data, calls `rag_tool.py` (Exa API), and commands `explanation_agent.py` to stream a structural breakdown to the UI sidebar.
[ ] Update the map dynamically on alert triggers, pivoting layout states from stable green to red alert zones.

- Judging Criteria Alignment: Maps to Human-in-the-Loop, Orchestration, and Story Arc Alignment by allowing the presenter/operator to force anomalies and observe the live multi-agent reaction.
- Success Criteria: Toggling the demo switch shifts the interface state smoothly from a standard profile to a red alert view with updated explanation panels and retrieval data.
- Tests: Verify session state mutations and that the end-to-end data pipeline completes successfully without UI freezing.

Part 7: Exa API Integration via RAG Tool

[ ] Integrate `rag_tool.py` with the external Exa API, routing requests securely using the `EXA_API_KEY`.
[ ] Construct targeted spatial search queries (weather anomalies, excavation permits, road closures) matching coordinates of flagged nodes.
[ ] Render the structured context headlines within the dedicated Exa sidebar/dashboard component.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Autonomy & Decision-Making by empowering the RAG tool to fetch real-world context for anomalous network locations.
- Success Criteria: Geospatial queries return clean, structured real-time local context relevant to the simulated coordinates.
- Tests: Mock API integration testing ensuring graceful handling of network timeouts or empty search results payloads.

Part 8: AI Chat Connectivity and Exception Handling

[ ] Configure the OpenAI API client framework using the secure `OPENAI_API_KEY` to drive agent reasoning.
[ ] Implement localized emergency failure handling: If external endpoints (OpenAI or Exa) timeout or fail, the Planner Agent catches the exception, activates a localized emergency state, maps the frontend to pure mathematical telemetry, and flashes a warning banner.

- Judging Criteria Alignment: Maps to Failure Handling and Orchestration by establishing fallback pathways for external services.
- Success Criteria: API exceptions do not crash the app, but instead trigger a clean downgrade to mathematical/local-only telemetry.
- Tests: Force connection timeouts or use invalid credentials and verify that the dashboard switches to emergency fallback mode with a warning banner.

Part 9: Prompt Engineering and Hub-and-Spoke Orchestration

[ ] Define the structured JSON schemas passed exclusively between the specialized agents and the central Planner Agent (avoiding global broadcasts).
[ ] Program prompt templates for each agent in `src/agents/` that define their roles, enforce the localized Plan-Execute-Reflect reasoning, and prevent defensive filler text.
[ ] Implement the asynchronous communication flow routing all specialist payloads strictly through the central Planner Agent.

- Judging Criteria Alignment: Maps to Orchestration and Autonomy & Decision-Making by establishing a clean Hub-and-Spoke communication layer.
- Success Criteria: Planner Agent coordinates simulation, risk, and explanation outputs purely using structured JSON payloads.
- Tests: Validate that structured JSON output schemas match input constraints for each agent.

Part 10: Streaming UI Sidebar & Human-in-the-Loop Integration

[ ] Implement a collapsible conversational chat sidebar in [app.py](file:///c:/Users/User/OneDrive - Universitat Ramón Llull/Desktop/2026-jobs/PUB/hackathon/src/app.py).
[ ] Use `st.write_stream` to stream the explanation agent's dispatch briefings and responses.
[ ] Implement operator review controls: allow the operator to override automated decisions, input custom conversational focus constraints, and approve/veto generated field dispatch logs before execution.
[ ] Implement simulation divergence handling: If the hydraulic solver encounters mathematical matrix division errors or numerical divergence during an aggressive scenario, the Simulation Agent catches the exception and falls back to pre-cached stable historical solver states.

- Judging Criteria Alignment: Maps to Human-in-the-Loop, Failure Handling, and Demo & Presentation by providing interactive control features, streaming outputs, and solver robustness.
- Success Criteria: Smooth, token-by-token sidebar text streaming and operational override controls without UI blocking or crashes.
- Tests: Run integration tests (using AppTest or Playwright) to confirm the app boots, executes scenarios, updates telemetry metrics, handles solver failures, and streams conversational text without runtime failures.