# Manager Agent Implementation

## Overview

The Manager Agent is the orchestration layer for Project Eirene's autonomous empathy response pipeline. It coordinates all sub-agents (Monitor, Strategy, Generation, Audit, Memory) and manages the complete execution flow.

## Key Features

### 1. Pipeline Initialization
- Validates system configuration
- Initializes all sub-agents in the correct sequence
- Creates cycle-specific trace directories
- Sets up initial pipeline state

### 2. Cycle Execution
- Executes complete pipeline: Monitor → Strategy → Generation → Audit → Memory
- Routes data between agents
- Maintains execution state
- Logs all actions via TraceLogger

### 3. Error Handling
- **Retry Logic**: Automatically retries failed operations up to 3 times with exponential backoff
- **Circuit Breaker**: Terminates after 5 consecutive cycle failures to prevent infinite loops
- **Graceful Degradation**: Skips failed cycles and continues operation
- **Comprehensive Logging**: All errors logged with stack traces and context

### 4. Observability
- All agent actions logged to `traces/` directory
- Organized by cycle ID for easy navigation
- Includes timestamps, agent identifiers, action types, and data
- Error traces include stack traces and context

## Usage

```python
from src.agents.manager import ManagerAgent
from src.models.config import SystemConfig

# Load configuration
config = SystemConfig.from_env()

# Initialize Manager Agent
manager = ManagerAgent(config)

# Initialize pipeline
state = manager.initialize_pipeline()

# Execute a cycle
result = manager.execute_cycle()

# Check result
if result == CycleResult.SUCCESS:
    print("Cycle completed successfully!")
```

## Architecture

```
ManagerAgent
├── initialize_pipeline()      # Set up all agents
├── execute_cycle()            # Run complete pipeline
├── route_to_next_agent()      # Pass data between agents
└── handle_agent_failure()     # Error recovery logic
```

## Trace File Structure

```
traces/
└── cycle_20260116_212639/
    ├── 01_manager_initialize_start.json
    ├── 02_manager_agent_initialized.json
    ├── ...
    ├── 14_manager_cycle_complete.json
    └── errors.json (if any errors occurred)
```

## Requirements Satisfied

- **Requirement 6.1**: Manager Agent initializes all sub-agents in correct sequence
- **Requirement 6.2**: Routes outputs between agents in the pipeline
- **Requirement 6.3**: Implements error handling with retry logic and graceful termination
- **Requirement 6.4**: Maintains execution flow: Monitor → Strategy → Generation → Audit → Memory
- **Requirement 7.1**: All agent actions logged to traces/ directory

## Testing

The implementation includes comprehensive unit tests covering:
- Pipeline initialization
- Cycle execution
- Data routing between agents
- Error handling and retry logic
- Circuit breaker functionality
- Trace logging

Run tests with:
```bash
pytest tests/test_manager_agent.py -v
```

## Next Steps

The Manager Agent provides the foundation for the pipeline. The next tasks will implement the actual sub-agents:
- Task 3.1: Monitor Agent (TinyFish MCP integration)
- Task 3.2: Strategy Agent (Yutori knowledge base)
- Task 4.1: Generation Agent (Freepik + ElevenLabs)
- Task 5.1: Audit Agent (Modulate API)
- Task 6.1: Memory Agent (Yutori API)
