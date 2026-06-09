### Proposed Scaffolding

```text
soar-water-quality-agent/
├── .env                                 # Secure environmental secrets (EXA_API_KEY, OPENAI_API_KEY)
├── .gitignore                           # Excludes local virtual environments and environmental secrets
├── agents.md                            # Master prompt and evaluation matrix answering criteria 1–6
├── Dockerfile                           # Multi-stage container instruction using uv for instant deployment
├── pyproject.toml                       # High-speed dependency configuration (torch, wntr, exa-py)
├── uv.lock                              # Deterministic dependency tree mapping to ensure parity
├── README.md                            # Executive project overview and launch procedures
├── requirements.txt                     # Standard fallback dependency matrix mapping
│
├── data/
│   ├── raw/
│   │   └── water_potability.csv         # Baseline CSV data tracking node potability telemetry
│   ├── epanet/
│   │   └── network.inp                  # Static EPANET water distribution network configuration file
│   └── processed/                       # Cached matrices and cleaned execution sensor states
│
├── models/
│   ├── potability_model.pkl             # Serialized classical ML classification model checkpoint
│   └── weights.pth                      # Pre-trained PyTorch physics-informed neural network weights
│
├── src/
│   ├── app.py                           # Single-page interactive Streamlit operator dashboard
│   │
│   ├── agents/                          # [Dimension 1 & 4] Specialized Agent Core Layer
│   │   ├── planner_agent.py             # Evaluates user intent and maps internal execution steps
│   │   ├── simulation_agent.py          # Coordinates structural state inputs with the physical solver
│   │   ├── risk_agent.py                # Interrogates PINN layers to isolate hidden pressure risks
│   │   └── explanation_agent.py         # Formulates natural-language anomaly briefings for operators
│   │
│   ├── tools/                           # [Dimension 3] Modular Operational Tool Layer
│   │   ├── epanet_tool.py               # WNTR simulation wrapper interacting with the C-compiled binary
│   │   ├── ml_model_tool.py             # Handles local evaluation calls to potability_model.pkl
│   │   ├── sensor_tool.py               # Manages structural array inputs from sparse pressure sensors
│   │   └── rag_tool.py                  # Streamlined Exa API web connector fetching real-time context
│   │
│   └── pipelines/                       # [Dimension 6] Compute Automation Boundaries
│       ├── train_potability_model.py    # Offline processing code to build or update model assets
│       └── run_water_quality_scenario.py # Deterministic end-to-end pipeline simulating anomalies
│
├── notebooks/                           # Experimental Research & Prototyping Sandboxes
│   ├── 01_train_potability_model.ipynb  # Exploratory data analysis and model training loops
│   └── 02_epanet_water_age_simulation.ipynb # Prototyping workspace for WNTR hydraulic evaluation
│
├── scripts/                             # Containerization and Lifecycle Automation Tools
│   ├── start-server.sh                  # Builds and spins up the local Docker container (Mac/Linux)
│   ├── start-server.bat                 # Builds and spins up the local Docker container (Windows)
│   ├── stop-server.sh                   # Gracefully deprovisions container infrastructure (Mac/Linux)
│   └── stop-server.bat                  # Gracefully deprovisions container infrastructure (Windows)
└── docs/
    └── plan.md                          # Primary implementation roadmap mapped with phase criteria
```
