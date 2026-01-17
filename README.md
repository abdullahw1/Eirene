# Project Eirene 🌿

**Autonomous Multi-Agent Empathy Response Network**

Project Eirene is an autonomous system that detects community-level digital stress signals and generates clinical-grade "Mindful Moment" video interventions through a self-improving empathy marketing pipeline. The system operates with zero human input from signal discovery to video intervention draft, using therapeutic frameworks (CBT/DBT) to ensure clinical validity.

## 🎯 Overview

Eirene implements a multi-agent architecture where five specialized agents work together to:
1. **Monitor** web sources for stress signals (TinyFish MCP + AgentQL)
2. **Strategy** maps signals to therapeutic frameworks (Yutori knowledge base)
3. **Generate** "Mindful Moment" videos with visuals and voiceovers (Freepik + ElevenLabs)
4. **Audit** content for quality and emotional safety (Modulate API)
5. **Memory** stores outcomes for continuous self-improvement (Yutori)

All coordinated by a **Manager Agent** that handles orchestration, error recovery, and observability.

## ✨ Key Features

- **Zero-Touch Autonomy**: Complete pipeline execution without human intervention
- **Clinical Validity**: All interventions grounded in CBT/DBT frameworks
- **Self-Improvement**: Learns from past interventions to refine content style and voice parameters
- **Quality-First**: Multi-layer auditing ensures therapeutic appropriateness
- **Full Observability**: Comprehensive trace logging for debugging and monitoring
- **Error Resilience**: Automatic retry logic, circuit breakers, and graceful degradation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Manager Agent                          │
│                    (Orchestration)                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Monitor    │───▶│   Strategy   │───▶│  Generation  │
│  (TinyFish)  │    │   (Yutori)   │    │(Freepik+EL)  │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │    Audit     │
                                        │  (Modulate)  │
                                        └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │    Memory    │
                                        │   (Yutori)   │
                                        └──────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- API keys for:
  - AgentQL (web scraping)
  - Freepik (image generation)
  - ElevenLabs (voice synthesis)
  - Modulate (emotional validation)
  - Yutori (knowledge base & memory) ✅ **Configured!**
  - Retool (optional: human oversight dashboard)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/eirene.git
   cd eirene
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (Yutori key already configured!)
   ```

### 🎨 Web Dashboard (Recommended!)

The easiest way to test the agents is through the interactive web dashboard:

```bash
# Start the dashboard
./start_dashboard.sh

# Or manually:
source .venv/bin/activate
PYTHONPATH=. python dashboard.py
```

Then open your browser to: **http://localhost:5001**

The dashboard provides:
- 🎯 Interactive agent testing with one-click samples
- 📊 Real-time results visualization
- 📝 Complete trace log viewing
- 🧪 Test individual agents or the complete pipeline

See [DASHBOARD_README.md](DASHBOARD_README.md) for detailed dashboard documentation.

### Configuration

Create a `.env` file with the following variables:

```bash
# API Keys
AGENTQL_API_KEY=your_key_here
FREEPIK_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
MODULATE_API_KEY=your_key_here
YUTORI_API_KEY=your_key_here
YUTORI_BASE_URL=https://api.yutori.ai

# Optional: Human-in-the-loop
RETOOL_API_KEY=your_key_here
RETOOL_WEBHOOK_URL=https://your-org.retool.com/api/webhook

# System Settings
TRACES_DIRECTORY=./traces
ENABLE_RETOOL_REVIEW=false
AUDIT_ALIGNMENT_THRESHOLD=0.75
MODULATE_CONFIDENCE_THRESHOLD=0.7
MAX_REGENERATION_ATTEMPTS=3
CYCLE_INTERVAL_SECONDS=300
VIDEO_DURATION_MIN=30
VIDEO_DURATION_MAX=60
```

## 📖 Usage

### Web Dashboard (Recommended)

The interactive web dashboard is the easiest way to test agents:

```bash
./start_dashboard.sh
# Open http://localhost:5001 in your browser
```

Features:
- Click-to-test agent interface
- Pre-loaded sample stress signals
- Real-time results display
- Complete trace log viewing

### Command Line Usage

#### Basic Example

```python
from src.agents.manager import ManagerAgent
from src.models.config import SystemConfig

# Load configuration from .env
config = SystemConfig.from_env()

# Initialize Manager Agent
manager = ManagerAgent(config)

# Initialize pipeline
state = manager.initialize_pipeline()
print(f"Pipeline initialized: {state.cycle_id}")

# Execute one complete cycle
result = manager.execute_cycle()
print(f"Cycle result: {result.value}")
```

### Run Demos

```bash
# Demo Manager Agent
python examples/demo_manager.py

# Demo Monitor and Strategy Agents
PYTHONPATH=. python examples/demo_monitor_strategy.py

# Web Dashboard (Interactive)
./start_dashboard.sh
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_manager_agent.py -v
```

## 📊 Current Implementation Status

### ✅ Completed
- **Task 1**: Project foundation and core data models
- **Task 2.1**: Manager Agent with pipeline orchestration
  - Pipeline initialization and coordination
  - Error handling with retry logic and circuit breaker
  - Complete trace logging system
  - Comprehensive unit tests
- **Task 3**: Monitor and Strategy Agents
  - **Task 3.1**: MonitorAgent with TinyFish MCP integration
    - Stress signal extraction and classification
    - Severity calculation and community context extraction
    - Full trace logging integration
  - **Task 3.2**: StrategyAgent with Yutori knowledge base integration
    - Therapeutic framework mapping (CBT/DBT)
    - Intervention specification generation
    - Content guidelines creation
  - 13 unit and integration tests, all passing
  - Demo script and comprehensive documentation

### 🚧 In Progress
- **Task 4**: Generation Agent (video composition)
- **Task 5**: Audit Agent (quality validation)
- **Task 6**: Memory Agent and end-to-end integration

## 📁 Project Structure

```
Eirene/
├── src/
│   ├── agents/          # Agent implementations
│   │   ├── manager.py   # Manager Agent (orchestration)
│   │   ├── monitor.py   # Monitor Agent (stress signal detection)
│   │   ├── strategy.py  # Strategy Agent (therapeutic mapping)
│   │   └── __init__.py
│   ├── models/          # Data models
│   │   ├── audit.py
│   │   ├── config.py
│   │   ├── intervention.py
│   │   ├── memory.py
│   │   ├── pipeline.py
│   │   └── stress_signal.py
│   └── utils/           # Utilities
│       └── trace_logger.py
├── tests/               # Test suite
│   ├── test_manager_agent.py
│   └── test_monitor_strategy_agents.py
├── examples/            # Example scripts
│   ├── demo_manager.py
│   └── demo_monitor_strategy.py
├── docs/                # Documentation
│   ├── manager_agent.md
│   └── monitor_strategy_agents.md
├── traces/              # Execution traces (gitignored)
├── .env.example         # Example environment config
├── requirements.txt     # Python dependencies
└── README.md
```

## 🔍 Observability

All agent actions are logged to the `traces/` directory, organized by cycle:

```
traces/
└── cycle_20260116_212639/
    ├── 01_manager_initialize_start.json
    ├── 02_manager_agent_initialized.json
    ├── ...
    ├── 14_manager_cycle_complete.json
    └── errors.json (if any errors occurred)
```

Each trace entry includes:
- Timestamp
- Cycle ID
- Agent identifier
- Action type
- Relevant data
- Status (success/failed/in_progress)

## 🤝 Contributing

This is a hackathon project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for [Hackathon Name]
- Powered by AgentQL, Freepik, ElevenLabs, Modulate, and Yutori APIs
- Inspired by the need for accessible mental health interventions

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This is an active development project. The system is designed for demonstration purposes and should not be used as a substitute for professional mental health care.
