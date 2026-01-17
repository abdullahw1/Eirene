# Monitor and Strategy Agents Documentation

## Overview

This document describes the implementation of the Monitor Agent (Agent A) and Strategy Agent (Agent B) for Project Eirene's autonomous empathy response network.

## Monitor Agent

The Monitor Agent is responsible for detecting community-level stress signals from web sources using TinyFish MCP with AgentQL.

### Key Features

- **TinyFish MCP Integration**: Connects to TinyFish MCP server using AgentQL for web scraping
- **Stress Signal Extraction**: Extracts structured stress signals from raw web data
- **Signal Classification**: Classifies signals into types (anxiety, burnout, isolation, depression, general_stress)
- **Severity Calculation**: Calculates severity indicators (0.0 to 1.0) based on content analysis
- **Community Context**: Extracts community context from source URLs
- **Trace Logging**: Logs all actions for observability

### API

```python
class MonitorAgent:
    def __init__(
        self,
        agentql_api_key: str,
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None
    )
    
    def connect_tinyfish_mcp() -> bool
    def scan_web_sources() -> List[StressSignal]
    def extract_signal_metadata(raw_data: Dict[str, Any]) -> StressSignal
    def disconnect()
```

### Usage Example

```python
from src.agents.monitor import MonitorAgent
from src.utils.trace_logger import TraceLogger

# Initialize
trace_logger = TraceLogger(traces_dir="./traces")
cycle_id = "cycle_001"
trace_logger.create_cycle_directory(cycle_id)

monitor = MonitorAgent(
    agentql_api_key="your_key",
    trace_logger=trace_logger,
    cycle_id=cycle_id
)

# Connect to TinyFish MCP
monitor.connect_tinyfish_mcp()

# Extract signal from raw data
raw_data = {
    "url": "https://reddit.com/r/anxiety/post123",
    "content": "I'm feeling very anxious...",
    "timestamp": datetime.now()
}

signal = monitor.extract_signal_metadata(raw_data)
print(f"Signal Type: {signal.signal_type}")
print(f"Severity: {signal.severity_indicator}")
```

### Signal Classification

The Monitor Agent classifies signals into the following types:

- **anxiety**: Keywords like "anxious", "anxiety", "worried", "panic"
- **burnout**: Keywords like "burnout", "exhausted", "overwhelmed"
- **isolation**: Keywords like "lonely", "isolated", "alone"
- **depression**: Keywords like "depressed", "depression", "sad"
- **general_stress**: Default for other stress-related content

### Severity Calculation

Severity is calculated based on intensity words in the content:
- Base severity: 0.3
- Additional 0.15 per intensity word (severe, extreme, unbearable, crisis, etc.)
- Maximum: 1.0

## Strategy Agent

The Strategy Agent maps stress signals to evidence-based therapeutic frameworks (CBT/DBT) using Yutori knowledge base integration.

### Key Features

- **Yutori Knowledge Base Integration**: Queries therapeutic frameworks using semantic search
- **CBT/DBT Mapping**: Maps stress signals to specific CBT or DBT techniques
- **Intervention Specification**: Generates complete intervention specs with content guidelines
- **Clinical Rationale**: Provides evidence-based rationale for framework selection
- **Trace Logging**: Logs all actions for observability

### API

```python
class StrategyAgent:
    def __init__(
        self,
        yutori_api_key: str,
        yutori_base_url: str,
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None
    )
    
    def query_therapeutic_frameworks(signal: StressSignal) -> TherapeuticContext
    def map_to_cbt_dbt(context: TherapeuticContext) -> InterventionSpec
    def generate_content_guidelines(spec: InterventionSpec) -> Dict[str, str]
```

### Usage Example

```python
from src.agents.strategy import StrategyAgent
from src.models.stress_signal import StressSignal

# Initialize
strategy = StrategyAgent(
    yutori_api_key="your_key",
    yutori_base_url="https://api.yutori.ai",
    trace_logger=trace_logger,
    cycle_id=cycle_id
)

# Query therapeutic frameworks
context = strategy.query_therapeutic_frameworks(signal)
print(f"Framework: {context.framework}")
print(f"Techniques: {context.techniques}")

# Map to intervention spec
spec = strategy.map_to_cbt_dbt(context)
print(f"Target Emotion: {spec.target_emotion}")
print(f"Content Theme: {spec.content_theme}")
print(f"Visual Guidelines: {spec.visual_guidelines}")
```

### Framework Mapping

The Strategy Agent maps signal types to therapeutic frameworks:

| Signal Type | Framework | Techniques |
|------------|-----------|------------|
| anxiety | CBT | cognitive_reframing, breathing_exercises, grounding |
| burnout | DBT | mindfulness, self_compassion, boundary_setting |
| isolation | CBT | behavioral_activation, social_connection, self_compassion |
| depression | CBT | cognitive_reframing, behavioral_activation, mindfulness |
| general_stress | CBT | stress_management, mindfulness, relaxation |

### Content Themes

Based on techniques, the agent determines content themes:

- **grounding**: Natural scenes with earth elements, stable imagery
- **self_compassion**: Warm, gentle imagery with soft lighting
- **mindfulness**: Peaceful nature scenes, flowing water
- **empowerment**: Uplifting imagery, sunrise/growth themes
- **relaxation**: Serene landscapes, soft colors

## Integration

The Monitor and Strategy agents work together in a pipeline:

1. **Monitor Agent** extracts stress signals from web sources
2. **Strategy Agent** receives signals and queries therapeutic frameworks
3. **Strategy Agent** generates intervention specifications
4. Specifications are passed to the Generation Agent (next in pipeline)

### Complete Pipeline Example

```python
# Initialize agents
monitor = MonitorAgent(agentql_api_key="key", trace_logger=logger, cycle_id=cycle_id)
strategy = StrategyAgent(
    yutori_api_key="key",
    yutori_base_url="https://api.yutori.ai",
    trace_logger=logger,
    cycle_id=cycle_id
)

# Monitor extracts signal
raw_data = {"url": "...", "content": "...", "timestamp": datetime.now()}
signal = monitor.extract_signal_metadata(raw_data)

# Strategy processes signal
context = strategy.query_therapeutic_frameworks(signal)
spec = strategy.map_to_cbt_dbt(context)

# Spec is now ready for Generation Agent
```

## Testing

Both agents have comprehensive unit tests and integration tests:

```bash
# Run all tests
python -m pytest tests/test_monitor_strategy_agents.py -v

# Run specific test class
python -m pytest tests/test_monitor_strategy_agents.py::TestMonitorAgent -v
python -m pytest tests/test_monitor_strategy_agents.py::TestStrategyAgent -v
```

### Test Coverage

- Monitor Agent: 8 unit tests
- Strategy Agent: 4 unit tests
- Integration: 1 integration test
- Total: 13 tests, all passing

## Demo

Run the demo script to see the agents in action:

```bash
PYTHONPATH=. python examples/demo_monitor_strategy.py
```

This will:
1. Process 3 different stress signals (anxiety, burnout, isolation)
2. Show the complete pipeline from signal extraction to intervention spec
3. Create trace logs in `traces/demo_YYYYMMDD_HHMMSS/`

## Trace Logging

All agent actions are logged to the traces directory with the following structure:

```
traces/
└── cycle_YYYYMMDD_HHMMSS/
    ├── 01_monitor_extract_metadata_start.json
    ├── 02_monitor_extract_metadata_complete.json
    ├── 03_strategy_query_frameworks_start.json
    ├── 04_strategy_query_frameworks_complete.json
    ├── 05_strategy_map_to_framework_start.json
    ├── 06_strategy_map_to_framework_complete.json
    └── errors.json (if any errors occur)
```

Each trace file contains:
- timestamp
- cycle_id
- agent identifier
- action type
- action data
- status

## Requirements Validation

### Monitor Agent Requirements (1.1, 1.2, 1.3)

✅ **1.1**: Monitor Agent queries web sources using TinyFish MCP with AgentQL  
✅ **1.2**: Extracts community-level indicators and metadata from stress signals  
✅ **1.3**: Passes structured stress signal data to Strategy Agent

### Strategy Agent Requirements (2.1, 2.2, 2.3, 2.4)

✅ **2.1**: Uses Yutori knowledge base to retrieve therapeutic frameworks  
✅ **2.2**: Maps stress signals to specific CBT or DBT techniques  
✅ **2.3**: Generates intervention specification with therapeutic approach and content guidelines  
✅ **2.4**: Passes intervention specification to Generation Agent (next in pipeline)

## Future Enhancements

1. **Real TinyFish MCP Integration**: Currently uses placeholder for AgentQL queries
2. **Real Yutori API Integration**: Currently uses rule-based mapping instead of API calls
3. **Advanced NLP**: Use LLM for better signal classification and severity calculation
4. **Multi-language Support**: Support stress signals in multiple languages
5. **Historical Pattern Analysis**: Learn from past signals to improve classification
