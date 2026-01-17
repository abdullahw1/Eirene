"""Demo: Strategy Agent → Generation Agent Pipeline"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.strategy import StrategyAgent
from src.agents.generation import GenerationAgent
from src.models.stress_signal import StressSignal
from src.utils.trace_logger import TraceLogger

# Load environment variables
load_dotenv()


def main():
    """Demo the Strategy → Generation pipeline"""
    
    print("=" * 80)
    print("PROJECT EIRENE - STRATEGY → GENERATION PIPELINE DEMO")
    print("=" * 80)
    print()
    
    # Initialize trace logger
    trace_logger = TraceLogger(traces_dir="./traces")
    cycle_id = "demo_pipeline"
    
    # Initialize agents
    print("Initializing agents...")
    
    strategy_agent = StrategyAgent(
        yutori_api_key=os.getenv("YUTORI_API_KEY", "demo_key"),
        yutori_base_url=os.getenv("YUTORI_BASE_URL", "https://api.yutori.ai"),
        trace_logger=trace_logger,
        cycle_id=cycle_id
    )
    
    generation_agent = GenerationAgent(
        freepik_api_key=os.getenv("FREEPIK_API_KEY", "demo_key"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "demo_key"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        output_dir="./generated_content",
        trace_logger=trace_logger,
        cycle_id=cycle_id
    )
    
    print("✓ Strategy Agent initialized")
    print("✓ Generation Agent initialized")
    print()
    
    # Create a sample stress signal (from Monitor Agent)
    stress_signal = StressSignal(
        source_url="https://reddit.com/r/college",
        signal_type="anxiety",
        community_context="College students expressing finals anxiety and academic pressure",
        severity_indicator=0.85,
        timestamp="2026-01-16T14:30:00Z",
        raw_content="Feeling overwhelmed with finals coming up. Can't sleep, constant worry..."
    )
    
    print("STRESS SIGNAL DETECTED")
    print("-" * 80)
    print(f"  Type: {stress_signal.signal_type}")
    print(f"  Severity: {stress_signal.severity_indicator * 100:.0f}%")
    print(f"  Context: {stress_signal.community_context}")
    print()
    
    # STEP 1: Strategy Agent - Map to therapeutic framework
    print("STEP 1: STRATEGY AGENT - Mapping to Therapeutic Framework")
    print("-" * 80)
    
    # Query therapeutic frameworks
    print("  [1/2] Querying Yutori knowledge base...")
    therapeutic_context = strategy_agent.query_therapeutic_frameworks(stress_signal)
    print(f"        ✓ Framework: {therapeutic_context.framework}")
    print(f"        ✓ Techniques: {', '.join(therapeutic_context.techniques)}")
    
    # Map to intervention spec
    print("  [2/2] Generating intervention specification...")
    intervention_spec = strategy_agent.map_to_cbt_dbt(therapeutic_context)
    print(f"        ✓ Target Emotion: {intervention_spec.target_emotion}")
    print(f"        ✓ Content Theme: {intervention_spec.content_theme}")
    print(f"        ✓ Framework: {intervention_spec.therapeutic_framework}")
    print()
    
    # STEP 2: Generation Agent - Create intervention
    print("STEP 2: GENERATION AGENT - Creating 'Mindful Moment' Video")
    print("-" * 80)
    
    try:
        # Generate visual
        print("  [1/5] Generating visual content...")
        visual = generation_agent.generate_visual(intervention_spec)
        print(f"        ✓ Visual saved: {Path(visual.image_url).name}")
        
        # Generate script
        print("  [2/5] Generating voiceover script...")
        script = generation_agent.generate_voiceover_script(intervention_spec, visual)
        print(f"        ✓ Script: {len(script.script_text.split())} words, {script.duration_seconds}s")
        print(f"        Preview: \"{script.script_text[:80]}...\"")
        
        # Get voice parameters
        print("  [3/5] Configuring voice parameters...")
        voice_params = generation_agent._get_voice_parameters(intervention_spec)
        print(f"        ✓ Voice ID: {voice_params.voice_id}")
        print(f"        ✓ Stability: {voice_params.stability}, Similarity: {voice_params.similarity_boost}")
        
        # Generate audio
        print("  [4/5] Generating audio with ElevenLabs...")
        try:
            audio = generation_agent.generate_audio(script, voice_params)
            print(f"        ✓ Audio saved: {Path(audio.audio_url).name}")
        except Exception as e:
            print(f"        ⚠ Using fallback audio (API key needed)")
            from src.models.intervention import AudioContent
            audio = AudioContent(
                audio_url="demo_audio.mp3",
                audio_data=b"demo",
                duration_seconds=script.duration_seconds,
                voice_parameters=voice_params,
                elevenlabs_metadata={"demo": True}
            )
        
        # Combine video
        print("  [5/5] Combining into video with ffmpeg...")
        try:
            video = generation_agent.combine_video(visual, audio)
            print(f"        ✓ Video saved: {Path(video.video_url).name}")
            print(f"        ✓ Duration: {video.duration_seconds}s")
            print(f"        ✓ Resolution: {video.resolution}")
        except Exception as e:
            print(f"        ⚠ Video composition skipped (ffmpeg needed)")
            print(f"        Error: {str(e)[:60]}")
        
        # Package intervention
        print()
        print("  [✓] INTERVENTION COMPLETE!")
        print()
        
        # Show final result
        print("FINAL INTERVENTION PACKAGE")
        print("-" * 80)
        print(f"  Therapeutic Framework: {intervention_spec.therapeutic_framework}")
        print(f"  Target Emotion: {intervention_spec.target_emotion}")
        print(f"  Content Theme: {intervention_spec.content_theme}")
        print(f"  Visual: {Path(visual.image_url).name}")
        print(f"  Script: {len(script.script_text.split())} words")
        print(f"  Audio: {Path(audio.audio_url).name}")
        if 'video' in locals():
            print(f"  Video: {Path(video.video_url).name}")
        print()
        print("  Full Script:")
        print("  " + "-" * 76)
        for line in script.script_text.split('. '):
            if line.strip():
                print(f"  {line.strip()}.")
        print()
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)
    print("PIPELINE DEMO COMPLETE")
    print("=" * 80)
    print()
    print("This demonstrates the complete flow:")
    print("  1. Monitor Agent detects stress signal (simulated)")
    print("  2. Strategy Agent maps to CBT/DBT framework")
    print("  3. Generation Agent creates 'Mindful Moment' video")
    print()
    print("Next: Wire into Manager Agent for full autonomous pipeline!")
    print()


if __name__ == "__main__":
    main()
