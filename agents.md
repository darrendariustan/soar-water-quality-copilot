# Soar Water Quality Agent Dashboard

## Business Requirements
- An MVP of a multi-agent physics-informed leak detection and water quality analysis application for utility distribution networks.
- The application consists of a single-page interactive operator dashboard built as a containerized Streamlit application driven by a decoupled multi-agent backend framework.
- The dashboard must display three key visual components: a geospatial network topology map showing a pressure/water-age heatmap, an anomaly alert panel detailing leak probabilities, potability indexes, and physics residual scores, and an Exa real-time context panel.
- Include an interactive demo flow layout with a control mechanism to trigger pre-configured "Injected Water Quality & Leak Scenarios" to contrast baseline normal operations against uncontained distribution anomalies.
- Triggering a simulation scenario must visibly update the network map to highlight the suspected risk zones, generate a structured plain-language explanation panel for operators, and update the retrieval panel with live contextual data.
- The system features a multi-agent conversational sidebar chat interface where autonomous specialized agents interpret telemetry exceptions, summarize mass-balance violations, and coordinate operational field documentation.
- No extra functionality: no arbitrary user account creation, no historical log search indices, no custom network topology graph editing. Keep it simple.
- The priority is a slick, professional, gorgeous engineering UI/UX with high scannability for utility operators.
- The app opens with a default stable, normal operating network data state pre-populated from static network and model checkpoints.

## Agent Configuration & Evaluation Archetype
1. Agent Overview
The architecture features a coordinated team of four specialized, autonomous agents located within src/agents/ that split the evaluation demands:
- Planner Agent (planner_agent.py): Acts as the central supervisor and executive router. It parses operator queries or UI event triggers, constructs sequential execution roadmaps, selects necessary tool chains, and delegates sub-tasks to downstream specialist agents.
- Simulation Agent (simulation_agent.py): Manages physical state calculations. It interfaces with hydraulic models and C-compiled network solvers to evaluate fluid velocity, water age, and system-wide mass-balance properties.
- Risk Agent (risk_agent.py): Evaluates structural and health threats. It executes forward-pass evaluations across machine learning models and physics-informed neural layers to isolate leak probabilities and potability anomalies from sparse sensor arrays.
- Explanation Agent (explanation_agent.py): Translates technical engineering parameters into operational text. It ingests mathematical tensor profiles, C-solver outputs, and web context strings to synthesize scannable, natural-language dispatch briefings for field crews.

2. Autonomy & Decision-Making
- Reasoning Framework: The multi-agent cluster operates on a localized Plan-Execute-Reflect loop. The Planner Agent evaluates incoming data anomalies or user queries, maps out data dependencies, and sequentially routes tasks using structured JSON control payloads without hardcoded paths.
- Tool-Use Patterns: Agents autonomously decide when and how to invoke operations based on telemetry limits. For example, if a simulation returns an abnormal pressure drop profile, the Planner Agent automatically instructs the Risk Agent to spin up machine learning evaluation pipelines, and instructs the Explanation Agent to dynamically alter its retrieval strategy based on localized junction identifiers.

3. Actions & Tool Use
Agents perform operations strictly by invoking isolated tools contained in `src/tools/`:
- EPANET Tool (epanet_tool.py): Wraps WNTR execution frameworks to programmatically interact with .inp network topologies, modifying nodes and extraction matrices on-the-fly.
- ML Model Tool (ml_model_tool.py): Loads and handles local evaluation checkpoints for classical classification parameters (potability_model.pkl) and deep physics-informed structural tensors.
- Sensor Tool (sensor_tool.py): Manages structural array mappings, downsampling high-density grid fields into sparse array feeds to simulate realistic hardware constraints.
- RAG Tool (rag_tool.py): Connects to the external Exa API, running targeted geospatial queries to pull localized real-time context (local road closures, weather anomalies, excavation permits) matching flagged coordinates.

4. Orchestration
- Coordination & Communication: The system utilizes a hierarchical Hub-and-Spoke communication architecture. Specialist agents do not broadcast states globally; instead, they communicate asynchronously via structured JSON schemas passed exclusively through the central Planner Agent.
- Delegation Flow:
    1. UI Scenario Trigger / Operator Text Query $\rightarrow$ Planner Agent.
    2. Planner Agent calls sensor_tool.py and delegates to Simulation Agent to isolate hydraulic changes.
    3. Simulation Agent processes state via epanet_tool.py and returns metrics to Planner Agent.
    4. Planner Agent passes metrics to Risk Agent, which calls ml_model_tool.py to evaluate potability and leak vectors.
    5. Planner Agent aggregates all engineering data, calls rag_tool.py, and commands Explanation Agent to stream a coherent structural breakdown to the UI sidebar.

5. Human-in-the-Loop
- Intervention Points: The utility operator retains absolute execution veto and override authority.
- UI Controls: The operator uses UI toggles in src/app.py to manually force simulated leak or potability incidents, inputs custom constraints to redirect conversational focus in the sidebar, and reviews/approves generated dispatch logs before they are marked for execution.

6. Failure Handling
- API Exceptions: If external endpoints (OpenAI, Exa API) time out or encounter token initialization failures, the Planner Agent intercepts the exception, activates a localized emergency state, maps the frontend to pure mathematical telemetry mode, and flashes a warning banner across the dashboard.
- Simulation Divergence: If the underlying hydraulic solver encounters mathematical matrix division errors or numerical divergence during an aggressive leak scenario, the Simulation Agent catches the loop exception, drops back to a pre-cached stable historical

7. Demo and Presentation
- Product Quality: Structured inside src/app.py using highly scannable UI layout components that divide the visual layer into real-time geospatial topology visualizers (via Plotly/PyVis), unified alert monitors, and an instantaneous streaming conversation sidebar (st.write_stream).
- Story Arc Alignment: Built to instantly pivot layout states from a green, stable operational landscape to an analytical red alert sequence the second an inspector interacts with the scenario panel to show high-fidelity product clarity during live evaluation panels.



## Technical Details
- Implemented as a containerized Streamlit application running on Python 3.11+.
- Packaged completely within a uniform multi-stage Dockerfile utilizing uv as the core package manager to guarantee deterministic, rapid cross-platform deployment of heavy binary files (torch, wntr).
- Source directories are structured cleanly to separate operational domains, positioning agents, pipelines, and tools into isolated modular script contexts under src/.
- No standalone database servers or persistent external volumes; operates using lightning-fast in-memory processing blocks and Streamlit state dictionaries (st.session_state) to eliminate thread-blocking and rendering delays.
- Utilizes Streamlit caching (st.cache_resource) on runtime boot to load static assets like trained model layers (models/potability_model.pkl) and EPANET graphs (data/epanet/network.inp) exactly once.
- Direct environment variables management ensures secure injection of API tokens (OPENAI_API_KEY, EXA_API_KEY) without leaking secrets to public source repositories.



## Strategy
1. Write plan with success criteria for each phase to be checked off. Include project scaffolding, Dockerfile configuration using uv, virtual environment setup, and basic validation testing for model loading and API client configuration.
2. Execute the plan ensuring all criteria are met
3. Carry out extensive integration testing with Streamlit AppTest or Playwright, fixing UI defects and rendering pipeline anomalies
4. Only complete when the MVP is finished and tested, with the containerized Streamlit server running locally and ready for the user



## Coding standards
1. Use latest versions of libraries and idiomatic approaches as of today
2. Keep it simple - NEVER over-engineer, ALWAYS simplify, NO unnecessary defensive programming. No extra features - focus on simplicity.
3. Be concise. Keep README minimal. IMPORTANT: no emojis ever
4. When hitting issues, always identify root cause before trying a fix. Do not guess. Prove with evidence, then fix the root cause.

# Working documentation
All documents for planning and executing this project will be in the docs/ directory.
Please review the docs/plan.md document before proceeding.