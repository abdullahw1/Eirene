"""Demo script for Manager Agent"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.manager import ManagerAgent
from src.models.config import SystemConfig


def main():
    """Demonstrate Manager Agent functionality"""
    
    # Create test configuration
    config = SystemConfig(
        agentql_api_key="demo_key",
        freepik_api_key="demo_key",
        elevenlabs_api_key="demo_key",
        modulate_api_key="demo_key",
        yutori_api_key="demo_key",
        yutori_base_url="https://api.yutori.ai",
        retool_api_key="demo_key",
        retool_webhook_url="https://demo.retool.com",
        traces_directory="./traces",
        enable_retool_review=False,
        audit_alignment_threshold=0.75,
        modulate_confidence_threshold=0.7,
        max_regeneration_attempts=3,
        cycle_interval_seconds=300,
        video_duration_min=30,
        video_duration_max=60
    )
    
    print("=" * 60)
    print("Project Eirene - Manager Agent Demo")
    print("=" * 60)
    print()
    
    # Initialize Manager Agent
    print("1. Initializing Manager Agent...")
    manager = ManagerAgent(config)
    
    # Initialize pipeline
    print("2. Initializing pipeline...")
    state = manager.initialize_pipeline()
    print(f"   ✓ Pipeline initialized with cycle ID: {state.cycle_id}")
    print(f"   ✓ Current agent: {state.current_agent.value}")
    print(f"   ✓ Status: {state.status.value}")
    print()
    
    # Execute a cycle
    print("3. Executing pipeline cycle...")
    result = manager.execute_cycle()
    print(f"   ✓ Cycle result: {result.value}")
    print(f"   ✓ Final status: {manager.current_state.status.value}")
    print()
    
    # Show trace information
    print("4. Trace information:")
    traces = manager.trace_logger.get_cycle_traces(state.cycle_id)
    print(f"   ✓ Total trace entries: {len(traces)}")
    print(f"   ✓ Trace directory: {config.traces_directory}/{state.cycle_id}")
    print()
    
    print("=" * 60)
    print("Demo complete! Check the traces directory for logs.")
    print("=" * 60)


if __name__ == "__main__":
    main()
