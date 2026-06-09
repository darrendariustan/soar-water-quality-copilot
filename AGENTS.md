# AquaPINN Operator Dashboard

## Business Requirements
- An MVP of a physics-informed leak detection assistant web application for water distribution networks
- The web app should consist of a single-page interactive operator dashboard built as a containerized Streamlit monolith
- The dashboard must display three key visual components: a network map showing a pressure heatmap, an anomaly alert panel detailing leak probability and physics residual scores, and an Exa real-time context panel
- Include an interactive demo flow layout with a control mechanism to trigger pre-configured "Injected Leak Scenarios" to clearly contrast baseline normal operations against uncontained leaks
- Triggering a leak scenario must visibly update the map to show the suspected leak zone, generate a plain-language explanation panel for operators, and update the Exa panel with live contextual data
- There is an AI chat feature in a sidebar; the AI assistant acts as an autonomous hydraulic operations translator capable of interpreting telemetry exceptions and coordinating field documentation
- No extra functionality: no user accounts, no historical log search, no custom network topology editing. Keep it simple.
- The priority is a slick, professional, gorgeous engineering UI/UX with high scannability for utility operators
- The app should open with a default stable, normal operating network data state pre-populated

## Agent Configuration & Evaluation Archetype
1. Agent Overview
- Name: Hydraulic Copilot
- Purpose: To act as an expert layer between raw engineering telemetry and the utility operator. It translates non-linear neural network predictions and mass-balance physics violations into plain-language diagnostic insights and field response recommendations.

2. Autonomy & Decision-Making
- Reasoning Framework: The agent employs a Reflection-and-Synthesis pattern. Upon a user query or a dashboard state change (leak triggered), it ingests the structural system state (node pressures, physics residuals, leak probabilities) and uses structured reasoning to determine whether external environmental data is required.
- Tool Selection: It autonomously builds targeted search string parameters to query external contexts when leak probabilities cross a critical engineering threshold (e.g., greater than 70%).

3. Actions & Tool Use
- Physics Engine Tool (WNTR/EPANET): Ingests live state data to calculate hydraulic continuity and mass balance errors.
- Inference Engine Tool (PyTorch PINN): Runs forward-pass evaluations to generate grid-wide pressure estimations and anomaly probabilities.
- Context Retrieval Tool (Exa API): Executes highly focused queries to pull regional geospatial web context (weather updates, local excavation filings, road closures).
- LLM Gateway Tool (OpenAI API): Drives conversational interactions using the openai/gpt-oss-120b system model wrapper.

4. Orchestration
- Architecture: Single-Agent Supervisor with tool-calling attachments. The Hydraulic Copilot maintains centralized executive control, sequentially querying the mathematical inference outputs, processing external text streams, and building unified operational responses.

5. Human-in-the-Loop
- Intervention Points: The operator maintains manual system override authority. The operator initiates the simulated leak vectors via the UI controls, inputs natural language queries to redirect the agent's analytical focus, and manually approves generated field dispatch action logs before final deployment.

6. Failure Handling
- API Exceptions: If the OpenRouter/OpenAI or Exa API pathways encounter latency timeouts or invalid tokens, the agent catches the error gracefully and defaults the dashboard views to pure mathematical telemetry mode with a clear warning notification banner.
- Physics Anomalies: If the underlying WNTR simulation encounters numerical divergence or matrix errors, the application isolates the simulation loop, relies purely on the pre-cached historical matrix data states, and logs the pipeline trace for engineering evaluation.

## Technical Details
- Implemented as a modern Streamlit application running on Python 3.11+
- Packaged completely within a Docker container to ensure cross-platform binary compatibility for deep learning and hydraulic simulation dependencies
- Use uv as the ultra-fast package manager for Python inside the Docker container to handle heavy wheels like torch and wntr efficiently
- The Streamlit application source code and Docker assets should be created in a subdirectory frontend
- Use Streamlit native streaming features (st.write_stream) for the AI chat sidebar to keep the user interface responsive during API call evaluation
- Use structured outputs in JSON format especially across multiple agents and APIs
- No database persistence and no separate backend server infrastructure; pure in-memory execution and direct API routing
- Load the pre-trained PyTorch PINN model weights (.pth) and the static EPANET network configuration file (.inp) directly into memory using Streamlit caching features on initialization
- Integrate the Exa API securely using environment variables to fetch external real-time context based on text queries relevant to the anomaly location
- Use popular visualization libraries such as Plotly or PyVis to handle interactive rendering of the 20 to 50 node water network topology
- As simple as possible but with an elegant corporate-utility UI

## Color Scheme
- Water Blue Primary: #209dd7 - links, key sections, normal pressure nodes
- Alert Red Accent: #e03e2d - high leak probability, anomaly highlights, structural leaks
- Residual Purple Secondary: #753991 - physics residual scores, mass-balance violations
- Dark Utility Navy: #032147 - main headings, sidebars, dashboard structural framing
- Muted Gray Text: #888888 - supporting telemetry labels, metadata text

Strategy
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
Please review the docs/PLAN.md document before proceeding.