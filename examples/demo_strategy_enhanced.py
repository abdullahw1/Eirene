"""Demo: Enhanced Strategy Agent with detailed intervention specs"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.agents.strategy import StrategyAgent
from src.models.stress_signal import StressSignal
from src.utils.trace_logger import TraceLogger

load_dotenv()

def demo_strategy_agent():
    """Demonstrate enhanced Strategy Agent capabilities"""
    
    print("🧠 Enhanced Strategy Agent Demo")
    print("=" * 80)
    print()
    
    # Initialize agent
    yutori_api_key = os.getenv("YUTORI_API_KEY", "demo_key")
    yutori_base_url = os.getenv("YUTORI_BASE_URL", "https://api.yutori.ai")
    
    trace_logger = TraceLogger(traces_dir="./traces")
    cycle_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    agent = StrategyAgent(
        yutori_api_key=yutori_api_key,
        yutori_base_url=yutori_base_url,
        trace_logger=trace_logger,
        cycle_id=cycle_id
    )
    
    # Test scenarios
    scenarios = [
        StressSignal(
            source_url="https://reddit.com/r/anxiety",
            signal_type="anxiety",
            community_context="Reddit community: r/anxiety - Finals week stress",
            severity_indicator=0.75,
            timestamp=datetime.now(),
            raw_content="I can't stop worrying about my exams. My heart is racing."
        ),
        StressSignal(
            source_url="https://twitter.com/worklife",
            signal_type="burnout",
            community_context="Twitter: Tech workers discussing burnout",
            severity_indicator=0.85,
            timestamp=datetime.now(),
            raw_content="I'm completely exhausted. Can't remember the last time I felt rested."
        ),
        StressSignal(
            source_url="https://forum.example.com/mental-health",
            signal_type="isolation",
            community_context="Mental health forum: Post-pandemic loneliness",
            severity_indicator=0.70,
            timestamp=datetime.now(),
            raw_content="I feel so alone. Haven't had a real conversation in weeks."
        )
    ]
    
    for i, signal in enumerate(scenarios, 1):
        print(f"Scenario {i}: {signal.signal_type.upper()}")
        print("-" * 80)
        print(f"Source: {signal.source_url}")
        print(f"Context: {signal.community_context}")
        print(f"Severity: {signal.severity_indicator:.0%}")
        print()
        
        # Query therapeutic frameworks
        print("🔍 Querying Therapeutic Frameworks...")
        context = agent.query_therapeutic_frameworks(signal)
        
        print(f"  Framework: {context.framework}")
        print(f"  Techniques: {', '.join(context.techniques)}")
        print(f"  Rationale: {context.clinical_rationale}")
        print()
        
        # Map to intervention spec
        print("📋 Generating Intervention Specification...")
        spec = agent.map_to_cbt_dbt(context)
        
        print(f"  Target Emotion: {spec.target_emotion}")
        print(f"  Content Theme: {spec.content_theme}")
        print()
        
        print("🎨 Visual Guidelines:")
        print(f"  {spec.visual_guidelines[:200]}...")
        print()
        
        print("📝 Text Guidelines:")
        print(f"  {spec.text_guidelines[:200]}...")
        print()
        
        print("🎯 Therapeutic Intent:")
        print(f"  {spec.therapeutic_intent}")
        print()
        
        print("=" * 80)
        print()
    
    print("✅ Demo Complete!")
    print(f"📁 Traces saved to: ./traces/{cycle_id}/")
    print()
    print("Key Enhancements:")
    print("  ✓ Detailed visual guidelines with specific prompts for Freepik")
    print("  ✓ Comprehensive text guidelines with structure and pacing")
    print("  ✓ Audio parameters for ElevenLabs voice generation")
    print("  ✓ Enhanced technique mapping (8 signal types)")
    print("  ✓ Clinical rationales for each framework selection")
    print("  ✓ Yutori integration for therapeutic knowledge retrieval")


if __name__ == "__main__":
    demo_strategy_agent()
