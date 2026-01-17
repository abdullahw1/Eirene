"""Demo script for Generation Agent"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.generation import GenerationAgent
from src.models.intervention import InterventionSpec
from src.utils.trace_logger import TraceLogger

# Load environment variables
load_dotenv()


def main():
    """Demo the Generation Agent"""
    
    print("=" * 80)
    print("PROJECT EIRENE - GENERATION AGENT DEMO")
    print("=" * 80)
    print()
    
    # Initialize trace logger
    trace_logger = TraceLogger(traces_dir="./traces")
    
    # Initialize Generation Agent
    print("Initializing Generation Agent...")
    agent = GenerationAgent(
        freepik_api_key=os.getenv("FREEPIK_API_KEY", "demo_key"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "demo_key"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        output_dir="./generated_content",
        trace_logger=trace_logger,
        cycle_id="demo_cycle"
    )
    print("✓ Generation Agent initialized")
    print()
    
    # Create sample intervention specs for different scenarios
    scenarios = [
        {
            "name": "Work Burnout",
            "spec": InterventionSpec(
                therapeutic_framework="DBT",
                target_emotion="self_acceptance",
                content_theme="self_compassion",
                visual_guidelines="Warm nurturing scene with gentle sunrise, soft golden light",
                text_guidelines="Use DBT-based language. Include self-compassion exercises. Warm, accepting tone.",
                therapeutic_intent="Apply DBT framework using self-compassion to support burnout recovery"
            )
        },
        {
            "name": "Finals Anxiety",
            "spec": InterventionSpec(
                therapeutic_framework="CBT",
                target_emotion="calm",
                content_theme="grounding",
                visual_guidelines="Natural grounding scene with forest floor, earth tones, soft lighting",
                text_guidelines="Use CBT-based language. Include breathing and grounding exercises.",
                therapeutic_intent="Apply CBT framework using grounding techniques to reduce anxiety"
            )
        },
        {
            "name": "Social Isolation",
            "spec": InterventionSpec(
                therapeutic_framework="CBT",
                target_emotion="motivation",
                content_theme="empowerment",
                visual_guidelines="Uplifting scene with sunrise over mountains, inspiring colors",
                text_guidelines="Use CBT-based language. Include behavioral activation and encouragement.",
                therapeutic_intent="Apply CBT framework using behavioral activation to address isolation"
            )
        }
    ]
    
    # Generate interventions for each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print("-" * 80)
        
        spec = scenario['spec']
        
        try:
            # Step 1: Generate visual
            print(f"  [1/5] Generating visual content ({spec.content_theme})...")
            visual = agent.generate_visual(spec)
            print(f"        ✓ Visual saved to: {visual.image_url}")
            
            # Step 2: Generate script
            print(f"  [2/5] Generating voiceover script...")
            script = agent.generate_voiceover_script(spec, visual)
            print(f"        ✓ Script generated ({len(script.script_text.split())} words, {script.duration_seconds}s)")
            print(f"        Preview: {script.script_text[:100]}...")
            
            # Step 3: Get voice parameters
            print(f"  [3/5] Configuring voice parameters...")
            voice_params = agent._get_voice_parameters(spec)
            print(f"        ✓ Voice: {voice_params.voice_id} (stability: {voice_params.stability})")
            
            # Step 4: Generate audio (will use fallback in demo without real API key)
            print(f"  [4/5] Generating audio with ElevenLabs...")
            try:
                audio = agent.generate_audio(script, voice_params)
                print(f"        ✓ Audio saved to: {audio.audio_url}")
            except Exception as e:
                print(f"        ⚠ Audio generation skipped (API key needed): {str(e)[:50]}")
                # Create mock audio for demo
                from src.models.intervention import AudioContent
                audio = AudioContent(
                    audio_url="demo_audio.mp3",
                    audio_data=b"demo",
                    duration_seconds=script.duration_seconds,
                    voice_parameters=voice_params,
                    elevenlabs_metadata={"demo": True}
                )
            
            # Step 5: Combine video (requires ffmpeg)
            print(f"  [5/5] Combining into video with ffmpeg...")
            try:
                video = agent.combine_video(visual, audio)
                print(f"        ✓ Video saved to: {video.video_url}")
                print(f"        Duration: {video.duration_seconds}s, Resolution: {video.resolution}")
            except Exception as e:
                print(f"        ⚠ Video composition skipped (ffmpeg needed): {str(e)[:50]}")
            
            # Package intervention
            print(f"  [✓] Intervention package complete!")
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            print()
            continue
    
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("Generated content saved to: ./generated_content/")
    print("Trace logs saved to: ./traces/")
    print()
    print("Next steps:")
    print("  1. Install ffmpeg: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
    print("  2. Add API keys to .env file:")
    print("     - FREEPIK_API_KEY")
    print("     - ELEVENLABS_API_KEY")
    print("     - OPENAI_API_KEY (optional, for better scripts)")
    print("  3. Run this demo again to generate real videos!")
    print()


if __name__ == "__main__":
    main()
