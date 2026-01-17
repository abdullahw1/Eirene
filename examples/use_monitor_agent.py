"""Example: How to use the Monitor Agent"""

from datetime import datetime
from src.agents.monitor import MonitorAgent
from src.utils.trace_logger import TraceLogger

# Initialize trace logger
trace_logger = TraceLogger(traces_dir="./traces")
cycle_id = f"example_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
trace_logger.create_cycle_directory(cycle_id)

# Initialize Monitor Agent
monitor = MonitorAgent(
    agentql_api_key="your_agentql_key",  # Or use demo key
    trace_logger=trace_logger,
    cycle_id=cycle_id
)

print("🔍 Monitor Agent Example")
print("=" * 60)

# Step 1: Connect to TinyFish MCP
print("\n1. Connecting to TinyFish MCP...")
monitor.connect_tinyfish_mcp()
print("   ✓ Connected!")

# Step 2: Prepare raw web data (simulating what AgentQL would extract)
print("\n2. Preparing test data...")
raw_data = {
    "url": "https://reddit.com/r/anxiety/post123",
    "content": "I've been feeling extremely anxious lately. Can't sleep at night, constant worry about everything. My heart races and I feel like I can't breathe sometimes.",
    "timestamp": datetime.now()
}
print(f"   URL: {raw_data['url']}")
print(f"   Content: {raw_data['content'][:60]}...")

# Step 3: Extract stress signal
print("\n3. Extracting stress signal...")
signal = monitor.extract_signal_metadata(raw_data)

# Step 4: Display results
print("\n4. Results:")
print("   " + "=" * 56)
print(f"   Signal Type:       {signal.signal_type}")
print(f"   Severity:          {signal.severity_indicator:.2f}")
print(f"   Community:         {signal.community_context}")
print(f"   Source URL:        {signal.source_url}")
print(f"   Timestamp:         {signal.timestamp}")
print("   " + "=" * 56)

# Step 5: View trace logs
print(f"\n5. Trace logs saved to: traces/{cycle_id}/")
traces = trace_logger.get_cycle_traces(cycle_id)
print(f"   Total trace entries: {len(traces)}")

print("\n✓ Monitor Agent example complete!")
print("\nNext steps:")
print("  - Pass this signal to the Strategy Agent")
print("  - Or run the complete pipeline with both agents")
