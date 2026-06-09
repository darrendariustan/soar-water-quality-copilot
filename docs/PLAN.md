# High Level Steps for Project

Part 1: Plan and Scaffolding Verification

[ ] Verify root directory layout and confirm agents.md is correctly placed within the project root directory to guide system behavior.
[ ] Establish target validation checks for mock data payloads.

- Judging Criteria Alignment: Maps to Agent Overview by validating the core identity, layout, and purpose of the Hydraulic Copilot before coding.
- Success Criteria: Engineering lead signs off on the execution architecture.
- Tests: Structural file existence check.

Part 2: Docker Infrastructure and Environment Setup

[ ] Write a Dockerfile inside the frontend/ directory utilizing multi-stage builds and uv to fetch torch and wntr.
[ ] Configure .env mappings for environmental secrets management.
[ ] Write localized execution scripts (start-server.sh, stop-server.sh, and Windows equivalents) inside a scripts/ directory.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Failure Handling by setting up the closed, cross-platform container sandbox environment that isolates OS-specific engineering dependencies.
- Success Criteria: Docker image compiles cleanly under 3 minutes; container runs a baseline "Hello World" Streamlit page accessible at localhost:8501.
- Tests: Execute container ping test; verify uv lockfile generation integrity.

Part 3: Static Asset Integration and Caching

[ ] Place network.inp and weights.pth within frontend/data/.
[ ] Implement st.cache_resource wrapper pipelines to load the EPANET topology via WNTR and model variables via PyTorch.

- Judging Criteria Alignment: Maps to Actions & Tool Use by binding the backend simulation and neural network environments as local execution tools.
- Success Criteria: App boots instantly without repeating heavy disk read routines on user window reruns.
- Tests: Assert model tensor weights match input channel parameters; verify WNTR parses network junctions without errors.

Part 4: Geospatial Network Dashboard Layout

[ ] Implement a single-page Streamlit view mapped to the Dark Utility Navy color scheme.
[ ] Integrate Plotly or PyVis to render the 20 to 50 node water distribution network tracking baseline pressure dimensions.
[ ] Structural layout setup for the 3 main columns: Map View, Telemetry Metrics Panel, and Exa Context Layer.

- Judging Criteria Alignment: Maps to Demo & Presentation by structuring a high-fidelity, scannable corporate utility dashboard.
- Success Criteria: Clean, responsive rendering of network nodes with scannable labels on canvas loading.
- Tests: Verification of visual element DOM mounting via Streamlit AppTest framework.

Part 5: Core Engineering Inference Implementation

[ ] Implement the forward-pass execution logic inside frontend/src/inference.py to calculate physics residuals and node leak probabilities.
[ ] Implement the WNTR wrapper logic inside frontend/src/simulation.py to capture baseline mass balance anomalies.

- Judging Criteria Alignment: Maps to Actions & Tool Use by giving the system the exact analytical instruments needed to calculate state physics and neural predictions.
- Success Criteria: Passing a mock 1D sensor tensor to the model returns valid float tensors for hidden pressure profiles without throwing runtime exceptions.
- Tests: Execute deterministic unit tests confirming output tensor structures map exactly to the number of network nodes.

Part 6: Injected Leak Scenario State Controls

[ ] Create UI control toggle variables within st.session_state to represent normal stable operations vs anomaly events.
[ ] Bind toggle interactions to update the map rendering dynamically, transitioning nodes to Alert Red when high leak probabilities are calculated.

- Judging Criteria Alignment: Maps to Human-in-the-Loop by providing the control dashboard interfaces that allow the presenter/operator to manually alter state realities.
- Success Criteria: Toggling the demo switch shifts the interface state smoothly from a standard profile to a flagged structural anomaly alert view.
- Tests: Verify UI state variables mutate correctly inside the global session scope upon toggle button triggers.

Part 7: Exa API Integration

[ ] Implement the API connector logic inside frontend/src/exa_api.py utilizing the secure EXA_API_KEY` environment mapping.
[ ] Construct targeted spatial search query templates based on flagged nodes to isolate local utilities issues or weather alerts.

- Judging Criteria Alignment: Maps to Actions & Tool Use and Autonomy & Decision-Making by empowering the agent to autonomously retrieve external web knowledge to enrich its internal dataset.
- Success Criteria: Triggering a query successfully renders a structured feed of context headlines within the dedicated Exa dashboard component.
- Tests: Mock API integration testing ensuring graceful handling of network timeouts or empty search results payloads.

Part 8: AI Chat Connectivity Setup

[ ] Configure the OpenAI API client framework targeting the openai/gpt-oss-120b system model instance.
[ ] Implement a baseline network connectivity sanity loop mapping a basic text command prompt routine.

- Judging Criteria Alignment: Maps to Agent Overview and Orchestration by validating core communication pathways with the single supervisor agent engine.
- Success Criteria: Executing the sanity verification pass yields a rapid structured response string from the target API gateway.
- Tests: Verify runtime authorization validation check against the endpoint using invalid credentials blocks progress gracefully.

Part 9: Engineering System Prompt Orchestration

[ ] Construct the master engineering prompt template wrapping full current operational parameters: topology dimensions, physics residual states, leak locations, and Exa context outputs.
[ ] Configure the system constraints to enforce concise hydraulic expert personas avoiding defensive text filler.

- Judging Criteria Alignment: Maps to Autonomy & Decision-Making by coding the exact system constraints and reasoning loops the agent uses to evaluate complex data profiles.
- Success Criteria: The conversational assistant consistently returns accurate, scannable breakdowns explaining mass-balance violations and operational responses.
- Tests: Validate prompt input length boundaries do not saturate context limit dimensions.

Part 10: Streaming UI Sidebar Implementation

[ ] Build a collapsible chat widget within the Streamlit sidebar surface interface.
[ ] Use st.write_stream execution targets to handle conversational streaming output variables directly on screen.
[ ] Bind context memory parameters across user session actions using persistent chat history structures.

- Judging Criteria Alignment: Maps to Demo & Presentation and Failure Handling by validating the end-to-end interactive demo story arc without suffering from UI freezing or uncaught exceptions.
- Success Criteria: Operators can query complex network characteristics or response criteria with smooth, token-by-token textual rendering without causing UI freezing.
- Tests: Run end-to-end integration passes utilizing Playwright to confirm the application loop boots, switches scenarios, pulls contextual updates, and streams conversational text without runtime failures.