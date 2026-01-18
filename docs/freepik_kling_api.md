# Freepik Kling 2.6 API Documentation

## Overview

Freepik provides the Kling 2.6 Pro API for AI-powered text-to-video and image-to-video generation. This is perfect for creating "Mindful Moment" videos from therapeutic imagery.

## API Key

Get your API key from [Freepik API Dashboard](https://www.freepik.com/api)

Store in `.env` as `FREEPIK_API_KEY=your_key_here`

## Endpoints

### 1. Create Image-to-Video Task

**Endpoint:** `POST https://api.freepik.com/v1/ai/image-to-video/kling-v2-6-pro`

**Headers:**
```
Content-Type: application/json
x-freepik-api-key: your_api_key_here
```

**Request Body:**
```json
{
  "prompt": "<string>",           // Description of desired video motion/animation
  "duration": "5",                // Video duration in seconds (5 or 10)
  "webhook_url": "<string>",      // Optional: URL to receive completion notification
  "negative_prompt": "<string>",  // Optional: What to avoid in the video
  "cfg_scale": 0.5,              // Guidance scale (0.0 to 1.0)
  "aspect_ratio": "widescreen_16_9", // Aspect ratio
  "generate_audio": true          // Whether to generate audio
}
```

**Example cURL:**
```bash
curl --request POST \
  --url https://api.freepik.com/v1/ai/image-to-video/kling-v2-6-pro \
  --header 'Content-Type: application/json' \
  --header 'x-freepik-api-key: your_api_key_here' \
  --data '{
    "prompt": "Gentle waves flowing on a peaceful beach at sunset",
    "duration": "5",
    "cfg_scale": 0.5,
    "aspect_ratio": "widescreen_16_9",
    "generate_audio": false
  }'
```

**Response:**
```json
{
  "task_id": "abc123...",
  "status": "pending",
  "created_at": "2026-01-16T14:30:00Z"
}
```

### 2. Get Status of All Tasks

**Endpoint:** `GET https://api.freepik.com/v1/ai/image-to-video/kling-v2-6`

**Headers:**
```
x-freepik-api-key: your_api_key_here
```

**Example cURL:**
```bash
curl --request GET \
  --url https://api.freepik.com/v1/ai/image-to-video/kling-v2-6 \
  --header 'x-freepik-api-key: your_api_key_here'
```

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "abc123...",
      "status": "completed",
      "video_url": "https://...",
      "created_at": "2026-01-16T14:30:00Z",
      "completed_at": "2026-01-16T14:35:00Z"
    }
  ]
}
```

## Parameters Explained

### `prompt`
- Description of the desired video motion/animation
- For therapeutic videos, use calming descriptions:
  - "Gentle flowing water with soft ripples"
  - "Peaceful clouds drifting slowly across the sky"
  - "Soft swaying grass in a meadow"
  - "Calm ocean waves at sunset"

### `duration`
- Options: `"5"` or `"10"` seconds
- For "Mindful Moment" videos, use 5 seconds per scene
- Can combine multiple 5-second clips for 30-60 second videos

### `aspect_ratio`
- Options:
  - `"widescreen_16_9"` - Standard widescreen (recommended)
  - `"square_1_1"` - Square format
  - `"portrait_9_16"` - Vertical/mobile format

### `cfg_scale`
- Range: 0.0 to 1.0
- Controls how closely the video follows the prompt
- Recommended: 0.5 for balanced results
- Higher values = more literal interpretation

### `generate_audio`
- `true` or `false`
- For our use case: `false` (we'll add ElevenLabs voiceover separately)

### `negative_prompt`
- Optional: Specify what to avoid
- Examples:
  - "harsh movements, sudden changes, jarring transitions"
  - "busy scenes, chaotic motion, fast pacing"

## Integration Strategy for Project Eirene

### Workflow

1. **Generate Static Image** (if needed)
   - Use Freepik image generation API first
   - Or use pre-existing therapeutic images

2. **Create Video from Image**
   - POST to `/image-to-video/kling-v2-6-pro`
   - Use therapeutic prompt from StrategyAgent
   - Set duration to 5 seconds
   - Use `widescreen_16_9` aspect ratio
   - Set `generate_audio: false`

3. **Poll for Completion**
   - GET `/image-to-video/kling-v2-6` to check status
   - Wait for `status: "completed"`
   - Download video from `video_url`

4. **Combine with Audio**
   - Use ffmpeg to merge Kling video with ElevenLabs audio
   - Create final "Mindful Moment" video

### Example Therapeutic Prompts

Based on StrategyAgent themes:

**Grounding:**
```
"Stable mountain landscape with gentle clouds, slow camera pan, peaceful and grounding atmosphere"
```

**Self-Compassion:**
```
"Warm sunrise with soft golden light spreading across the scene, gentle and nurturing movement"
```

**Mindfulness:**
```
"Flowing stream with gentle ripples, meditative and present-moment focus, calm water movement"
```

**Empowerment:**
```
"Sunrise over mountains with light gradually illuminating the peaks, uplifting and inspiring motion"
```

**Relaxation:**
```
"Peaceful beach at twilight with soft waves, serene and tranquil atmosphere, slow gentle motion"
```

## UI Integration Notes

The user mentioned: "this should be intuitive in the ui"

### Dashboard Integration Ideas

1. **Video Generation Status**
   - Show real-time status: "Generating video..." with progress indicator
   - Display task_id for tracking
   - Show estimated completion time (typically 2-5 minutes)

2. **Preview Section**
   - Embed video player when completed
   - Show thumbnail before video loads
   - Play button with controls

3. **Generation Parameters Display**
   - Show prompt used
   - Display duration, aspect ratio
   - Show cfg_scale setting

4. **Retry/Regenerate Button**
   - Allow regeneration with different prompts
   - Keep history of generated videos

## Cost Considerations

- Each video generation costs credits
- Monitor usage through Freepik dashboard
- Consider pre-generating demo videos to save costs during hackathon

## Testing

Create a test script:
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY")

# Test video generation
url = "https://api.freepik.com/v1/ai/image-to-video/kling-v2-6-pro"
headers = {
    "Content-Type": "application/json",
    "x-freepik-api-key": FREEPIK_API_KEY
}
payload = {
    "prompt": "Gentle waves on a peaceful beach at sunset",
    "duration": "5",
    "cfg_scale": 0.5,
    "aspect_ratio": "widescreen_16_9",
    "generate_audio": False
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

## Next Steps for Implementation

1. Create `FreepikKlingClient` class in `src/utils/`
2. Implement video generation in Generation Agent (Task 3.4)
3. Add polling mechanism for task completion
4. Integrate with dashboard for real-time status
5. Test with therapeutic prompts from StrategyAgent

## Notes

- Kling 2.6 Pro is the latest version with best quality
- Video generation typically takes 2-5 minutes
- Consider using webhooks for async notification
- Store generated videos locally for demo playback
