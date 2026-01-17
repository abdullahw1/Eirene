"""Generate a complete demo video with real API calls"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.generation import GenerationAgent
from src.models.intervention import InterventionSpec
from src.utils.trace_logger import TraceLogger

# Load environment variables
load_dotenv()


def main():
    """Generate a complete demo video"""
    
    print("=" * 80)
    print("GENERATING COMPLETE 'MINDFUL MOMENT' VIDEO")
    print("=" * 80)
    print()
    
    # Check API keys
    freepik_key = os.getenv("FREEPIK_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not freepik_key or freepik_key == "demo_key":
        print("⚠ Warning: FREEPIK_API_KEY not set, will use placeholder image")
    else:
        print(f"✓ Freepik API key found: {freepik_key[:10]}...")
    
    if not elevenlabs_key or elevenlabs_key == "demo_key":
        print("⚠ Warning: ELEVENLABS_API_KEY not set, will use fallback audio")
    else:
        print(f"✓ ElevenLabs API key found: {elevenlabs_key[:10]}...")
    
    print()
    
    # Initialize trace logger
    trace_logger = TraceLogger(traces_dir="./traces")
    
    # Initialize Generation Agent
    print("Initializing Generation Agent...")
    agent = GenerationAgent(
        freepik_api_key=freepik_key,
        elevenlabs_api_key=elevenlabs_key,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        output_dir="./generated_content",
        trace_logger=trace_logger,
        cycle_id="demo_video_generation"
    )
    print("✓ Generation Agent initialized")
    print()
    
    # Create intervention spec for "Finals Anxiety"
    print("Creating intervention specification...")
    spec = InterventionSpec(
        therapeutic_framework="CBT",
        target_emotion="calm",
        content_theme="grounding",
        visual_guidelines=(
            "Natural grounding scene with forest floor, moss, stones, earth tones, "
            "soft natural lighting, calming therapeutic illustration, high resolution"
        ),
        text_guidelines=(
            "Use CBT-based therapeutic language. Include gentle breathing exercises. "
            "Guide grounding: 'Notice 5 things you can see, 4 you can touch, 3 you can hear'. "
            "Structure: Opening (5-10s) - acknowledge anxiety, "
            "Middle (20-40s) - breathing and grounding exercise, "
            "Closing (5-10s) - affirmation. "
            "Keep language simple, direct, and supportive. "
            "Target 30-60 seconds total spoken duration. "
            "Tone: warm, calm, reassuring."
        ),
        therapeutic_intent=(
            "Apply CBT framework using grounding and breathing techniques to reduce "
            "finals anxiety and bring student back to present moment awareness"
        )
    )
    print(f"✓ Spec created: {spec.therapeutic_framework} - {spec.content_theme}")
    print()
    
    # Generate complete intervention
    print("GENERATING INTERVENTION")
    print("-" * 80)
    
    try:
        # Step 1: Generate visual
        print("[1/5] Generating visual content with Freepik...")
        visual = agent.generate_visual(spec)
        print(f"      ✓ Visual saved: {visual.image_url}")
        print(f"      Prompt: {visual.generation_prompt[:80]}...")
        print()
        
        # Step 2: Generate script
        print("[2/5] Generating voiceover script...")
        script = agent.generate_voiceover_script(spec, visual)
        print(f"      ✓ Script generated: {len(script.script_text.split())} words, {script.duration_seconds}s")
        print(f"      Pacing: {script.pacing}")
        print()
        print("      Full Script:")
        print("      " + "-" * 72)
        for line in script.script_text.split('. '):
            if line.strip():
                print(f"      {line.strip()}.")
        print()
        
        # Step 3: Get voice parameters
        print("[3/5] Configuring voice parameters...")
        voice_params = agent._get_voice_parameters(spec)
        print(f"      ✓ Voice ID: {voice_params.voice_id}")
        print(f"      ✓ Stability: {voice_params.stability}")
        print(f"      ✓ Similarity Boost: {voice_params.similarity_boost}")
        print()
        
        # Step 4: Generate audio with ElevenLabs
        print("[4/5] Generating audio with ElevenLabs...")
        print("      (This may take 10-20 seconds...)")
        audio = agent.generate_audio(script, voice_params)
        print(f"      ✓ Audio saved: {audio.audio_url}")
        print(f"      ✓ Duration: {audio.duration_seconds:.1f}s")
        print()
        
        # Step 5: Combine into video with ffmpeg
        print("[5/5] Combining into video with ffmpeg...")
        print("      (This may take 10-20 seconds...)")
        video = agent.combine_video(visual, audio)
        print(f"      ✓ Video saved: {video.video_url}")
        print(f"      ✓ Duration: {video.duration_seconds:.1f}s")
        print(f"      ✓ Resolution: {video.resolution}")
        if video.thumbnail_url:
            print(f"      ✓ Thumbnail: {video.thumbnail_url}")
        print()
        
        # Package intervention
        intervention = agent.package_intervention(video, script, visual, audio, spec)
        
        print("=" * 80)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("=" * 80)
        print()
        print(f"Video Location: {video.video_url}")
        print(f"Video Size: {len(video.video_data) / (1024 * 1024):.2f} MB")
        print()
        print("You can now:")
        print(f"  1. Play the video: open {video.video_url}")
        print(f"  2. View in Finder: open {Path(video.video_url).parent}")
        print(f"  3. Use in dashboard for demo")
        print()
        
        # Offer to play the video
        print("Opening video in default player...")
        import subprocess
        subprocess.run(["open", video.video_url])
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
