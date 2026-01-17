"""Demo script for Monitor and Strategy Agents"""

from datetime import datetime
from src.agents.monitor import MonitorAgent
from src.agents.strategy import StrategyAgent
from src.utils.trace_logger import TraceLogger


def main():
    """Demonstrate Monitor and Strategy agents working together"""
    
    print("=" * 60)
    print("Project Eirene - Monitor & Strategy Agents Demo")
    print("=" * 60)
    print()
    
    # Initialize trace logger
    trace_logger = TraceLogger(traces_dir="./traces")
    cycle_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    trace_logger.create_cycle_directory(cycle_id)
    
    # Initialize agents
    print("Initializing agents...")
    monitor = MonitorAgent(
        agentql_api_key="demo_key",
        trace_logger=trace_logger,
        cycle_id=cycle_id
    )
    
    strategy = StrategyAgent(
        yutori_api_key="demo_key",
        yutori_base_url="https://api.yutori.ai",
        trace_logger=trace_logger,
        cycle_id=cycle_id
    )
    print("✓ Agents initialized\n")
    
    # Simulate web data from different sources
    test_cases = [
        {
            "url": "https://reddit.com/r/anxiety/post123",
            "content": "I've been feeling extremely anxious lately. Can't sleep, constant worry.",
            "timestamp": datetime.now()
        },
        {
            "url": "https://reddit.com/r/burnout/post456",
            "content": "Completely burned out from work. Exhausted all the time.",
            "timestamp": datetime.now()
        },
        {
            "url": "https://forum.example.com/isolation",
            "content": "Feeling so lonely and isolated. No one to talk to.",
            "timestamp": datetime.now()
        }
    ]
    
    # Process each test case
    for i, raw_data in enumerate(test_cases, 1):
        print(f"Test Case {i}: {raw_data['url']}")
        print("-" * 60)
        
        # Step 1: Monitor Agent extracts stress signal
        print("📡 Monitor Agent: Extracting stress signal...")
        signal = monitor.extract_signal_metadata(raw_data)
        
        print(f"  Signal Type: {signal.signal_type}")
        print(f"  Severity: {signal.severity_indicator:.2f}")
        print(f"  Community: {signal.community_context}")
        print()
        
        # Step 2: Strategy Agent queries therapeutic frameworks
        print("🧠 Strategy Agent: Querying therapeutic frameworks...")
        context = strategy.query_therapeutic_frameworks(signal)
        
        print(f"  Framework: {context.framework}")
        print(f"  Techniques: {', '.join(context.techniques)}")
        print()
        
        # Step 3: Strategy Agent maps to intervention spec
        print("📋 Strategy Agent: Creating intervention specification...")
        spec = strategy.map_to_cbt_dbt(context)
        
        print(f"  Target Emotion: {spec.target_emotion}")
        print(f"  Content Theme: {spec.content_theme}")
        print(f"  Visual Guidelines: {spec.visual_guidelines[:80]}...")
        print(f"  Therapeutic Intent: {spec.therapeutic_intent[:80]}...")
        print()
        print("=" * 60)
        print()
    
    print("✓ Demo complete!")
    print(f"\nTrace logs saved to: {trace_logger.traces_dir}")


if __name__ == "__main__":
    main()
