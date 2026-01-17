# Generation Agent Documentation

## Overview

The Generation Agent (Agent C) is responsible for creating complete "Mindful Moment" video interventions from therapeutic specifications. It orchestrates visual generation, voiceover script creation, audio synthesis, and video composition into a cohesive therapeutic intervention.

## Architecture

```
InterventionSpec (from Strategy Agent)
    ↓
[1] Generate Visual (Freepik API)
    ↓
[2] Generate Voiceover Script (OpenAI/Anthropic/Templates)
    ↓
[3] Generate Audio (ElevenLabs API)
    ↓
[4] Combine Video (ffmpeg)
    ↓
[5] Package Intervention
    ↓
Complete Intervention Package
```

## Components

### 1. Visual Generation

**Purpose**: Generate calming, therapeutic images using Freepik API

**Features**:
- Theme-based prompt templates (grounding, self-compassion, mindfulness, empowerment, relaxation)
- Automatic prompt optimization for therapeutic content
- Fallback to gradient placeholder images if API unavailable
- 1920x1080 resolution for video composition

**Themes**:
- **Grounding**: Natural scenes with earth tones, forest floors, stones
- **Self-Compassion**: Warm sunrise scenes with golden light
- **Mindfulness**: Flowing water, zen gardens, minimalist aesthetics
- **Empowerment**: Mountain sunrises, uplifting growth imagery
- **Relaxation**: Still lakes, peaceful meadows, soft clouds

### 2. Voiceover Script Generation

**Purpose**: Create 30-60 second therapeutic scripts

**Structure**:
1. **Opening (5-10s)**: Acknowledge the feeling/situation with empathy
2. **Middle (20-40s)**: Guide through therapeutic technique or exercise
3. **Closing (5-10s)**: Provide affirmation or encouragement

**Generation Methods**:
1. **OpenAI GPT-4** (preferred): High-quality, contextual scripts
2. **Anthropic Claude** (fallback): Alternative LLM option
3. **Template-based** (fallback): Pre-written therapeutic scripts

**Features**:
- Framework-aware (CBT/DBT)
- Target emotion alignment
- Therapeutic language patterns
- Emphasis point extraction
- Duration calculation (30-60 seconds)

### 3. Audio Generation

**Purpose**: Convert scripts to calming voiceovers using ElevenLabs

**Voice Parameters**:
- **Stability**: 0.65 (balanced consistency)
- **Similarity Boost**: 0.75 (natural sound)
- **Voice Selection**: Emotion-based voice mapping
  - Calm: Rachel (21m00Tcm4TlvDq8ikWAM)
  - Self-acceptance: Bella (EXAVITQu4vr4xnSDxMaL)
  - Motivation: Adam (pNInz6obpgDQGcFmaJgB)

**Features**:
- High-quality MP3 output
- Therapeutic voice tone optimization
- Duration estimation
- Fallback to silent audio if API unavailable

### 4. Video Composition

**Purpose**: Combine image and audio into MP4 video using ffmpeg

**Features**:
- 1920x1080 resolution
- Subtle zoom effect for visual interest
- Fade in/out transitions (1 second each)
- Audio synchronization
- Thumbnail generation

**ffmpeg Command**:
```bash
ffmpeg -loop 1 -i image.png -i audio.mp3 \
  -c:v libx264 -tune stillimage \
  -c:a aac -b:a 192k \
  -vf "scale=1920:1080,zoompan=z='min(zoom+0.0015,1.1)',fade=in:0:1,fade=out" \
  -shortest -t duration output.mp4
```

### 5. Intervention Packaging

**Purpose**: Bundle all components into complete intervention

**Includes**:
- Intervention ID (unique identifier)
- Original specification
- Video content (MP4 file)
- Voiceover script (text + metadata)
- Audio content (MP3 file)
- Visual content (image file)
- Creation timestamp
- Metadata JSON file

## API Integration

### Freepik API

**Endpoint**: `POST https://api.freepik.com/v1/ai/text-to-image`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "x-freepik-api-key": "FPSX..."
}
```

**Payload**:
```json
{
  "prompt": "Calming therapeutic scene...",
  "num_images": 1,
  "image_size": "1024x1024",
  "styling": {
    "mode": "realistic",
    "quality": "high"
  }
}
```

### ElevenLabs API

**Endpoint**: `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`

**Headers**:
```json
{
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": "..."
}
```

**Payload**:
```json
{
  "text": "Script text...",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.65,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": true
  }
}
```

### OpenAI API (Optional)

**Endpoint**: `POST https://api.openai.com/v1/chat/completions`

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer sk-..."
}
```

**Payload**:
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a licensed therapist..."},
    {"role": "user", "content": "Create a script for..."}
  ],
  "temperature": 0.7,
  "max_tokens": 300
}
```

## Usage Example

```python
from src.agents.generation import GenerationAgent
from src.models.intervention import InterventionSpec
from src.utils.trace_logger import TraceLogger

# Initialize agent
agent = GenerationAgent(
    freepik_api_key="FPSX...",
    elevenlabs_api_key="...",
    openai_api_key="sk-...",  # Optional
    output_dir="./generated_content",
    trace_logger=TraceLogger(traces_dir="./traces"),
    cycle_id="cycle_001"
)

# Create intervention spec (from Strategy Agent)
spec = InterventionSpec(
    therapeutic_framework="CBT",
    target_emotion="calm",
    content_theme="grounding",
    visual_guidelines="Natural grounding scene...",
    text_guidelines="Use CBT-based language...",
    therapeutic_intent="Apply CBT framework..."
)

# Generate complete intervention
intervention = agent.generate_intervention(spec)

# Access components
print(f"Video: {intervention.video.video_url}")
print(f"Duration: {intervention.video.duration_seconds}s")
print(f"Script: {intervention.voiceover_script.script_text}")
```

## Output Structure

```
generated_content/
├── images/
│   └── visual_abc123.png
├── audio/
│   └── audio_def456.mp3
├── videos/
│   ├── mindful_moment_ghi789.mp4
│   └── mindful_moment_ghi789_thumb.jpg
└── intervention_xyz_metadata.json
```

## Error Handling

### Graceful Degradation

1. **Freepik API Failure**: Falls back to gradient placeholder images
2. **OpenAI/Anthropic Failure**: Falls back to template-based scripts
3. **ElevenLabs API Failure**: Falls back to silent audio placeholder
4. **ffmpeg Not Installed**: Provides clear error message with installation instructions

### Retry Logic

- API calls: 3 retries with exponential backoff
- Network timeouts: 60 seconds for generation, 30 seconds for downloads
- Trace logging: All errors logged to traces directory

## Dependencies

### Required
- `requests`: API calls
- `Pillow`: Image processing (fallback)
- `python-dotenv`: Environment configuration

### External Tools
- `ffmpeg`: Video composition (must be installed separately)

### Optional
- OpenAI API key: Better script generation
- Anthropic API key: Alternative script generation

## Configuration

### Environment Variables

```bash
FREEPIK_API_KEY=FPSX...
ELEVENLABS_API_KEY=...
OPENAI_API_KEY=sk-...        # Optional
ANTHROPIC_API_KEY=...        # Optional
```

### Agent Parameters

```python
GenerationAgent(
    freepik_api_key: str,           # Required
    elevenlabs_api_key: str,        # Required
    openai_api_key: Optional[str],  # Optional
    anthropic_api_key: Optional[str], # Optional
    output_dir: str = "./generated_content",
    trace_logger: Optional[TraceLogger] = None,
    cycle_id: Optional[str] = None
)
```

## Testing

Run tests:
```bash
pytest tests/test_generation_agent.py -v
```

Run demo:
```bash
python examples/demo_generation.py
```

## Performance

### Typical Generation Times

- Visual generation: 5-15 seconds (Freepik API)
- Script generation: 2-5 seconds (OpenAI) or instant (templates)
- Audio generation: 3-10 seconds (ElevenLabs)
- Video composition: 5-15 seconds (ffmpeg)
- **Total**: 15-45 seconds per intervention

### Resource Usage

- Disk space: ~5-10 MB per intervention
- Memory: ~100-200 MB during generation
- CPU: Moderate (ffmpeg video encoding)

## Future Enhancements

1. **Yutori Integration**: Retrieve historical style parameters for self-improvement
2. **Kling Video API**: Use Freepik's Kling API for animated videos instead of static images
3. **Batch Generation**: Generate multiple interventions in parallel
4. **Quality Metrics**: Track generation quality scores over time
5. **Custom Voices**: Train custom ElevenLabs voices for specific therapeutic styles
6. **Multi-language**: Support for non-English therapeutic content

## Troubleshooting

### ffmpeg Not Found

**Error**: `ffmpeg is not installed or not in PATH`

**Solution**:
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `apt-get install ffmpeg`
- Windows: Download from https://ffmpeg.org/

### API Rate Limits

**Error**: `429 Too Many Requests`

**Solution**:
- Add delays between requests
- Implement exponential backoff
- Use pre-generated content for demos

### Low Quality Audio

**Issue**: Audio sounds robotic or unnatural

**Solution**:
- Adjust stability (lower = more expressive)
- Try different voice IDs
- Use speaker boost feature
- Ensure script has natural pacing

### Video Composition Fails

**Error**: `ffmpeg failed: ...`

**Solution**:
- Check image format (PNG/JPG supported)
- Verify audio format (MP3/WAV supported)
- Ensure sufficient disk space
- Check ffmpeg version (4.0+ recommended)

## Support

For issues or questions:
1. Check trace logs in `./traces/` directory
2. Review error messages in console output
3. Verify API keys are valid and have credits
4. Ensure ffmpeg is installed and accessible

