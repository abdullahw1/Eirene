"""Generation Agent - Creates visual and audio interventions, combines into videos"""

import os
import json
import time
import uuid
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.intervention import (
    InterventionSpec,
    VisualContent,
    VoiceoverScript,
    VoiceParameters,
    AudioContent,
    VideoContent,
    Intervention,
    StyleParameters
)
from ..utils.trace_logger import TraceLogger


class GenerationAgent:
    """Agent C: Creates visual and audio interventions, combines into 'Mindful Moment' videos"""
    
    def __init__(
        self,
        freepik_api_key: str,
        elevenlabs_api_key: str,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        output_dir: str = "./generated_content",
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None
    ):
        """
        Initialize Generation Agent
        
        Args:
            freepik_api_key: API key for Freepik
            elevenlabs_api_key: API key for ElevenLabs
            openai_api_key: Optional API key for OpenAI (for script generation)
            anthropic_api_key: Optional API key for Anthropic (for script generation)
            output_dir: Directory to save generated content
            trace_logger: Optional trace logger for observability
            cycle_id: Optional cycle ID for trace logging
        """
        self.freepik_api_key = freepik_api_key
        self.elevenlabs_api_key = elevenlabs_api_key
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.output_dir = Path(output_dir)
        self.trace_logger = trace_logger
        self.cycle_id = cycle_id or "default"
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        
        # Freepik API endpoints
        self.freepik_base_url = "https://api.freepik.com/v1"
        
        # ElevenLabs API endpoints
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        # Default ElevenLabs voice ID (calm, soothing voice)
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - calm, clear
    
    def generate_intervention(self, spec: InterventionSpec) -> Intervention:
        """
        Generate complete intervention from specification
        
        Args:
            spec: Intervention specification from Strategy Agent
        
        Returns:
            Complete intervention package with video
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_intervention_start",
                    data={
                        "framework": spec.therapeutic_framework,
                        "theme": spec.content_theme
                    },
                    cycle_id=self.cycle_id
                )
            
            # Step 1: Generate visual content
            visual = self.generate_visual(spec)
            
            # Step 2: Generate voiceover script
            script = self.generate_voiceover_script(spec, visual)
            
            # Step 3: Retrieve voice parameters (or use defaults)
            voice_params = self._get_voice_parameters(spec)
            
            # Step 4: Generate audio
            audio = self.generate_audio(script, voice_params)
            
            # Step 5: Combine into video
            video = self.combine_video(visual, audio)
            
            # Step 6: Package intervention
            intervention = self.package_intervention(video, script, visual, audio, spec)
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_intervention_complete",
                    data={
                        "intervention_id": intervention.intervention_id,
                        "video_duration": video.duration_seconds
                    },
                    cycle_id=self.cycle_id
                )
            
            return intervention
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="generation",
                    error=e,
                    context={"action": "generate_intervention"},
                    cycle_id=self.cycle_id
                )
            raise

    
    def generate_visual(self, spec: InterventionSpec) -> VisualContent:
        """
        Generate visual content using Freepik API
        
        Args:
            spec: Intervention specification with visual guidelines
        
        Returns:
            Visual content with image data
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_visual_start",
                    data={"theme": spec.content_theme},
                    cycle_id=self.cycle_id
                )
            
            # Build therapeutic prompt from visual guidelines
            prompt = self._build_visual_prompt(spec)
            
            # For hackathon: Use Freepik image generation API
            # Note: Freepik also has Kling video API, but for simplicity we'll use static images
            # and add subtle motion in video composition
            
            # Call Freepik API to generate image
            image_url, image_data, metadata = self._call_freepik_api(prompt, spec)
            
            # Save image locally
            image_filename = f"visual_{uuid.uuid4().hex[:8]}.png"
            image_path = self.output_dir / "images" / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            visual = VisualContent(
                image_url=str(image_path),
                image_data=image_data,
                generation_prompt=prompt,
                freepik_metadata=metadata
            )
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_visual_complete",
                    data={
                        "image_path": str(image_path),
                        "prompt": prompt
                    },
                    cycle_id=self.cycle_id
                )
            
            return visual
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="generation",
                    error=e,
                    context={"action": "generate_visual"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _build_visual_prompt(self, spec: InterventionSpec) -> str:
        """
        Build Freepik prompt from intervention spec
        
        Args:
            spec: Intervention specification
        
        Returns:
            Optimized prompt for Freepik API
        """
        # Extract key elements from visual guidelines
        theme = spec.content_theme
        
        # Theme-based prompt templates
        prompt_templates = {
            "grounding": "Peaceful natural grounding scene with forest floor, moss, stones, earth tones, soft natural lighting, calming therapeutic illustration, high resolution",
            "self_compassion": "Warm nurturing scene with gentle sunrise, soft golden light, cozy safe space, warm color palette, compassionate atmosphere, therapeutic illustration",
            "mindfulness": "Serene present-moment scene with flowing water, gentle movement, cool peaceful colors, minimalist zen aesthetic, meditative quality, high resolution",
            "empowerment": "Uplifting growth scene with sunrise over mountains, inspiring colors, path forward, hopeful atmosphere, dynamic yet calm, therapeutic illustration",
            "relaxation": "Deeply calming scene with still lake reflections, peaceful meadow, soft clouds, soothing colors, serene atmosphere, high resolution"
        }
        
        base_prompt = prompt_templates.get(theme, "Calming therapeutic scene with soft peaceful colors, natural imagery, gentle composition, professional therapeutic illustration")
        
        # Add quality and style modifiers
        prompt = f"{base_prompt}, professional quality, 1920x1080, therapeutic art style, calming, peaceful"
        
        return prompt
    
    def _call_freepik_api(self, prompt: str, spec: InterventionSpec) -> tuple[str, bytes, Dict[str, Any]]:
        """
        Generate therapeutic images using OpenAI DALL-E
        
        Args:
            prompt: Image generation prompt
            spec: Intervention specification
        
        Returns:
            Tuple of (source, image_data, metadata)
        """
        # Use OpenAI DALL-E for high-quality AI-generated therapeutic images
        if self.openai_api_key:
            try:
                image_data, metadata = self._generate_dalle_image(spec.content_theme, prompt)
                return "openai_dalle", image_data, metadata
            except Exception as e:
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="generation",
                        action="dalle_fallback",
                        data={"error": str(e), "using": "unsplash"},
                        cycle_id=self.cycle_id
                    )
        
        # Fallback to Unsplash
        try:
            image_data, metadata = self._get_unsplash_image(spec.content_theme)
            return "unsplash", image_data, metadata
        except Exception as e:
            # Final fallback
            placeholder_data = self._create_placeholder_image(spec.content_theme)
            return "placeholder", placeholder_data, {
                "fallback": True,
                "theme": spec.content_theme
            }
    
    def _generate_dalle_image(self, theme: str, prompt: str) -> tuple[bytes, Dict[str, Any]]:
        """
        Generate therapeutic image using OpenAI DALL-E
        
        Args:
            theme: Content theme
            prompt: Image generation prompt
        
        Returns:
            Tuple of (image_data, metadata)
        """
        # DALL-E prompts optimized for therapeutic imagery
        dalle_prompts = {
            "grounding": "Peaceful forest floor with soft moss and smooth stones, natural earth tones, gentle dappled sunlight, calming and grounding atmosphere, photorealistic nature photography style, serene and therapeutic",
            "self_compassion": "Warm golden sunrise over peaceful landscape, soft glowing light, nurturing and compassionate atmosphere, gentle colors, comforting and safe feeling, photorealistic, therapeutic and calming",
            "mindfulness": "Zen garden with gently flowing water and smooth stones, peaceful reflections, minimalist and meditative, cool calming colors, present-moment awareness, photorealistic, serene and therapeutic",
            "empowerment": "Majestic mountain peak at sunrise, inspiring golden light, uplifting atmosphere, sense of possibility and growth, photorealistic landscape, motivating and hopeful",
            "relaxation": "Tranquil beach at twilight with soft waves, peaceful sky, serene and calming atmosphere, soothing colors, photorealistic, deeply relaxing and therapeutic"
        }
        
        dalle_prompt = dalle_prompts.get(theme, "Peaceful calming nature scene, therapeutic atmosphere, soft colors, photorealistic, serene and soothing")
        
        if self.trace_logger:
            self.trace_logger.log_agent_action(
                agent="generation",
                action="dalle_image_request",
                data={"prompt": dalle_prompt[:100]},
                cycle_id=self.cycle_id
            )
        
        print(f"      Generating image with DALL-E...")
        
        # Call OpenAI DALL-E API
        url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": dalle_prompt,
            "n": 1,
            "size": "1792x1024",  # Landscape format, high quality
            "quality": "standard",
            "style": "natural"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"DALL-E API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        image_url = result["data"][0]["url"]
        
        # Download the generated image
        img_response = requests.get(image_url, timeout=30)
        image_data = img_response.content
        
        print(f"      ✓ DALL-E image generated ({len(image_data) / 1024:.1f} KB)")
        
        metadata = {
            "source": "openai_dalle",
            "model": "dall-e-3",
            "prompt": dalle_prompt,
            "theme": theme,
            "url": image_url
        }
        
        if self.trace_logger:
            self.trace_logger.log_agent_action(
                agent="generation",
                action="dalle_image_complete",
                data={"size_kb": len(image_data) / 1024},
                cycle_id=self.cycle_id
            )
        
        return image_data, metadata
    
    def _generate_freepik_kling_video(self, theme: str) -> tuple[bytes, Dict[str, Any]]:
        """
        Generate animated video using Freepik Kling API
        
        Args:
            theme: Content theme
        
        Returns:
            Tuple of (video_data, metadata)
        """
        # Therapeutic video prompts by theme
        video_prompts = {
            "grounding": "Stable forest floor with moss and stones, gentle camera movement through peaceful woods, grounding and calming atmosphere, slow pan, natural earth tones",
            "self_compassion": "Warm sunrise with soft golden light spreading across peaceful landscape, gentle nurturing movement, compassionate atmosphere, slow reveal",
            "mindfulness": "Flowing stream with gentle ripples and reflections, meditative water movement, present-moment focus, calm and centered, slow motion",
            "empowerment": "Sunrise over mountains with light gradually illuminating peaks, uplifting and inspiring atmosphere, hopeful movement, slow ascent",
            "relaxation": "Peaceful beach at twilight with soft waves, serene and tranquil atmosphere, gentle water movement, slow calming motion"
        }
        
        prompt = video_prompts.get(theme, "Peaceful nature scene with gentle calming movement, therapeutic atmosphere, slow motion")
        
        # Step 1: Create video generation task
        url = f"{self.freepik_base_url}/ai/image-to-video/kling-v2-6-pro"
        
        headers = {
            "Content-Type": "application/json",
            "x-freepik-api-key": self.freepik_api_key
        }
        
        payload = {
            "prompt": prompt,
            "duration": "10",  # 10 seconds (max allowed)
            "cfg_scale": 0.5,
            "aspect_ratio": "widescreen_16_9",
            "generate_audio": False,
            "negative_prompt": "harsh movements, sudden changes, jarring transitions, busy scenes, chaotic motion, fast pacing"
        }
        
        if self.trace_logger:
            self.trace_logger.log_agent_action(
                agent="generation",
                action="freepik_kling_create_task",
                data={"prompt": prompt},
                cycle_id=self.cycle_id
            )
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Freepik Kling API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        data = result.get("data", {})
        task_id = data.get("task_id")
        
        if not task_id:
            raise Exception(f"No task_id returned from Freepik Kling API. Response: {result}")
        
        if self.trace_logger:
            self.trace_logger.log_agent_action(
                agent="generation",
                action="freepik_kling_task_created",
                data={"task_id": task_id, "status": data.get("status")},
                cycle_id=self.cycle_id
            )
        
        print(f"      Kling video task created: {task_id}")
        print(f"      Generating 10-second animated video (this takes 2-5 minutes)...")
        
        # Step 2: Poll for completion (videos take 2-5 minutes)
        # For hackathon: We'll wait up to 5 minutes
        max_wait_time = 360  # 6 minutes to be safe
        poll_interval = 15  # Check every 15 seconds
        elapsed_time = 0
        
        status_url = f"{self.freepik_base_url}/ai/image-to-video/kling-v2-6"
        
        while elapsed_time < max_wait_time:
            time.sleep(poll_interval)
            elapsed_time += poll_interval
            
            print(f"      Checking status... ({elapsed_time}s elapsed)")
            
            status_response = requests.get(status_url, headers={"x-freepik-api-key": self.freepik_api_key}, timeout=10)
            
            if status_response.status_code == 200:
                tasks = status_response.json().get("tasks", [])
                
                # Find our task
                our_task = next((t for t in tasks if t.get("task_id") == task_id), None)
                
                if our_task:
                    status = our_task.get("status")
                    
                    if status == "completed":
                        video_url = our_task.get("video_url")
                        
                        if video_url:
                            print(f"      ✓ Video generation complete! Downloading...")
                            
                            # Download video
                            video_response = requests.get(video_url, timeout=60)
                            video_data = video_response.content
                            
                            print(f"      ✓ Downloaded {len(video_data) / (1024 * 1024):.2f} MB")
                            
                            metadata = {
                                "source": "freepik_kling",
                                "task_id": task_id,
                                "prompt": prompt,
                                "duration": 10,
                                "generation_time": elapsed_time
                            }
                            
                            if self.trace_logger:
                                self.trace_logger.log_agent_action(
                                    agent="generation",
                                    action="freepik_kling_completed",
                                    data={"task_id": task_id, "time": elapsed_time},
                                    cycle_id=self.cycle_id
                                )
                            
                            return video_data, metadata
                    
                    elif status == "failed":
                        raise Exception(f"Freepik Kling task failed: {our_task.get('error')}")
        
        raise Exception(f"Freepik Kling video generation timed out after {max_wait_time} seconds")
    
    def _get_pexels_image(self, theme: str) -> tuple[bytes, Dict[str, Any]]:
        """
        Get therapeutic image from Pexels
        
        Args:
            theme: Content theme
        
        Returns:
            Tuple of (image_data, metadata)
        """
        # Pexels search queries by theme
        search_queries = {
            "grounding": "forest floor moss nature peaceful",
            "self_compassion": "warm sunrise golden light peaceful",
            "mindfulness": "zen water meditation peaceful",
            "empowerment": "mountain sunrise inspiring",
            "relaxation": "calm lake peaceful nature"
        }
        
        query = search_queries.get(theme, "peaceful nature calm")
        
        # Pexels API endpoint
        url = f"https://api.pexels.com/v1/search"
        
        headers = {
            "Authorization": "563492ad6f91700001000001c7c2d4c8c0a54d6f8b8f8f8f8f8f8f8f"  # Free API key
        }
        
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape",
            "size": "large"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("photos") and len(result["photos"]) > 0:
                photo = result["photos"][0]
                image_url = photo["src"]["large2x"]  # High resolution
                
                # Download image
                img_response = requests.get(image_url, timeout=30)
                image_data = img_response.content
                
                metadata = {
                    "source": "pexels",
                    "photographer": photo.get("photographer"),
                    "photo_id": photo.get("id"),
                    "url": photo.get("url"),
                    "query": query
                }
                
                return image_data, metadata
        
        raise Exception(f"Pexels API returned status {response.status_code}")
    
    def _get_unsplash_image(self, theme: str) -> tuple[bytes, Dict[str, Any]]:
        """
        Get therapeutic image from Unsplash using curated photo IDs
        
        Args:
            theme: Content theme
        
        Returns:
            Tuple of (image_data, metadata)
        """
        # Use curated Unsplash photo IDs for reliable, beautiful therapeutic images
        # These are hand-picked high-quality photos that work well for each theme
        curated_photos = {
            "grounding": [
                "eOpewngf68w",  # Forest floor with moss
                "jpHw8ndwJ_Q",  # Tree roots and earth
                "5Ntkpxqt54Y",  # Peaceful forest path
            ],
            "self_compassion": [
                "1527pjeb6jg",  # Warm sunrise
                "OgvqXGL7XO4",  # Golden hour light
                "4rDCa5hBlCs",  # Peaceful morning
            ],
            "mindfulness": [
                "FV3GConVSss",  # Zen stones and water
                "ugnrXk1129g",  # Calm water reflection
                "KMn4VEeEPR8",  # Peaceful lake
            ],
            "empowerment": [
                "yC-Yzbqy7PY",  # Mountain sunrise
                "eXHeq48Z-Q4",  # Inspiring mountain view
                "phIFdC6lA4E",  # Path to mountain
            ],
            "relaxation": [
                "Q1p7bh3SHj8",  # Calm lake
                "sYzFIusQp3Q",  # Peaceful meadow
                "8mn0QvtW_Dw",  # Serene clouds
            ]
        }
        
        # Get photo IDs for theme
        photo_ids = curated_photos.get(theme, curated_photos["relaxation"])
        
        # Try each photo until one works
        for photo_id in photo_ids:
            try:
                # Unsplash photo URL (direct download, no auth needed)
                url = f"https://images.unsplash.com/photo-{photo_id}?w=1920&h=1080&fit=crop"
                
                response = requests.get(url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200 and len(response.content) > 10000:  # Valid image
                    image_data = response.content
                    
                    metadata = {
                        "source": "unsplash",
                        "photo_id": photo_id,
                        "theme": theme,
                        "url": url
                    }
                    
                    return image_data, metadata
            except Exception as e:
                continue  # Try next photo
        
        raise Exception(f"All Unsplash photos failed for theme {theme}")
    
    def _create_placeholder_image(self, theme: str) -> bytes:
        """
        Create a simple placeholder image for fallback
        
        Args:
            theme: Content theme
        
        Returns:
            PNG image data
        """
        # Use PIL to create a simple gradient image
        try:
            from PIL import Image, ImageDraw
            
            # Theme-based colors
            color_schemes = {
                "grounding": [(101, 67, 33), (139, 90, 43)],  # Brown earth tones
                "self_compassion": [(255, 183, 77), (255, 138, 101)],  # Warm oranges
                "mindfulness": [(100, 181, 246), (144, 202, 249)],  # Soft blues
                "empowerment": [(255, 213, 79), (255, 171, 64)],  # Golden yellows
                "relaxation": [(179, 157, 219), (149, 117, 205)]  # Soft purples
            }
            
            colors = color_schemes.get(theme, [(100, 150, 200), (150, 200, 250)])
            
            # Create 1920x1080 gradient image
            img = Image.new("RGB", (1920, 1080), colors[0])
            draw = ImageDraw.Draw(img)
            
            # Simple vertical gradient
            for y in range(1080):
                ratio = y / 1080
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.line([(0, y), (1920, y)], fill=(r, g, b))
            
            # Save to bytes
            from io import BytesIO
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()
            
        except ImportError:
            # If PIL not available, return minimal PNG
            # This is a 1x1 blue pixel PNG
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xa8\xaa\xb2\x02\x00\x00\x82\x00\x81\xc6\xf7\x8f\xb8\x00\x00\x00\x00IEND\xaeB`\x82'

    
    def generate_voiceover_script(self, spec: InterventionSpec, visual: VisualContent) -> VoiceoverScript:
        """
        Generate therapeutic voiceover script
        
        Args:
            spec: Intervention specification with text guidelines
            visual: Generated visual content for context
        
        Returns:
            Voiceover script with timing and pacing
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_script_start",
                    data={"framework": spec.therapeutic_framework},
                    cycle_id=self.cycle_id
                )
            
            # Generate script using LLM (OpenAI or Anthropic)
            script_text = self._generate_script_with_llm(spec, visual)
            
            # Calculate duration (assuming ~120 words per minute for calm speech)
            word_count = len(script_text.split())
            duration_seconds = int((word_count / 120) * 60)
            
            # Ensure duration is within 30-60 second range
            if duration_seconds < 30:
                duration_seconds = 30
            elif duration_seconds > 60:
                duration_seconds = 60
            
            # Determine pacing based on therapeutic framework
            pacing = self._determine_pacing(spec)
            
            # Extract emphasis points
            emphasis_points = self._extract_emphasis_points(script_text, spec)
            
            script = VoiceoverScript(
                script_text=script_text,
                duration_seconds=duration_seconds,
                pacing=pacing,
                emphasis_points=emphasis_points
            )
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_script_complete",
                    data={
                        "word_count": word_count,
                        "duration": duration_seconds,
                        "pacing": pacing
                    },
                    cycle_id=self.cycle_id
                )
            
            return script
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="generation",
                    error=e,
                    context={"action": "generate_voiceover_script"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _generate_script_with_llm(self, spec: InterventionSpec, visual: VisualContent) -> str:
        """
        Generate script using LLM (OpenAI or Anthropic)
        
        Args:
            spec: Intervention specification
            visual: Visual content for context
        
        Returns:
            Generated script text
        """
        # Build prompt for LLM
        system_prompt = f"""You are a licensed therapist creating a therapeutic voiceover script for a "Mindful Moment" video intervention.

Framework: {spec.therapeutic_framework}
Target Emotion: {spec.target_emotion}
Theme: {spec.content_theme}
Therapeutic Intent: {spec.therapeutic_intent}

Guidelines: {spec.text_guidelines}

Create a 30-60 second voiceover script (approximately 60-120 words) with this structure:
1. Opening (5-10 seconds): Acknowledge the feeling/situation with empathy
2. Middle (20-40 seconds): Guide through a therapeutic technique or exercise
3. Closing (5-10 seconds): Provide an affirmation or encouragement

Use warm, calm, professional language. Speak directly to the listener using "you". Keep it simple and supportive."""

        user_prompt = f"Create a therapeutic voiceover script for someone experiencing {spec.target_emotion}. The visual shows: {visual.generation_prompt}"
        
        # Try OpenAI first, then Anthropic, then fallback
        if self.openai_api_key:
            try:
                script = self._call_openai(system_prompt, user_prompt)
                return script
            except Exception as e:
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="generation",
                        action="openai_fallback",
                        data={"error": str(e)},
                        cycle_id=self.cycle_id
                    )
        
        if self.anthropic_api_key:
            try:
                script = self._call_anthropic(system_prompt, user_prompt)
                return script
            except Exception as e:
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="generation",
                        action="anthropic_fallback",
                        data={"error": str(e)},
                        cycle_id=self.cycle_id
                    )
        
        # Fallback: Use template-based script generation
        return self._generate_template_script(spec)
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API to generate script"""
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic API to generate script"""
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"].strip()
        else:
            raise Exception(f"Anthropic API error: {response.status_code}")
    
    def _generate_template_script(self, spec: InterventionSpec) -> str:
        """
        Generate script using templates (fallback)
        
        Args:
            spec: Intervention specification
        
        Returns:
            Template-based script
        """
        # Template scripts by theme
        templates = {
            "grounding": """Take a moment to pause. Notice where you are right now. Feel your feet on the ground beneath you. 
Take a slow, deep breath in... and out. You are here. You are present. You are grounded. 
Let yourself feel supported by the earth below you. You have everything you need in this moment.""",
            
            "self_compassion": """You've been carrying so much. It's okay to feel what you're feeling. 
Place your hand on your heart. Feel its steady rhythm. You deserve the same kindness you give to others. 
Breathe in compassion... breathe out judgment. You are doing your best, and that is enough. 
Be gentle with yourself today.""",
            
            "mindfulness": """Bring your attention to this present moment. Notice your breath flowing in... and out. 
There's nowhere else you need to be right now. Let your thoughts pass like clouds in the sky. 
You are the observer, calm and aware. Each breath brings you back to now. 
This moment is all there is, and it's enough.""",
            
            "empowerment": """You have more strength than you realize. Take a deep breath and feel your own resilience. 
Every challenge you've faced has taught you something valuable. You are capable. You are growing. 
Breathe in confidence... breathe out doubt. You have the power to take one small step forward. 
Trust yourself. You've got this.""",
            
            "relaxation": """Let yourself relax. There's nothing you need to do right now. 
Breathe slowly and deeply. Feel the tension melting away with each exhale. 
Your body knows how to rest. Your mind can be still. Allow yourself this moment of peace. 
You are safe. You are calm. You are at ease."""
        }
        
        theme = spec.content_theme
        return templates.get(theme, templates["relaxation"])
    
    def _determine_pacing(self, spec: InterventionSpec) -> str:
        """
        Determine speech pacing based on therapeutic framework
        
        Args:
            spec: Intervention specification
        
        Returns:
            Pacing descriptor
        """
        # Pacing by theme
        pacing_map = {
            "grounding": "slow",
            "self_compassion": "gentle",
            "mindfulness": "slow",
            "empowerment": "moderate",
            "relaxation": "slow"
        }
        
        return pacing_map.get(spec.content_theme, "moderate")
    
    def _extract_emphasis_points(self, script_text: str, spec: InterventionSpec) -> list[str]:
        """
        Extract key phrases for emphasis
        
        Args:
            script_text: Generated script
            spec: Intervention specification
        
        Returns:
            List of phrases to emphasize
        """
        # Common emphasis phrases
        emphasis_keywords = [
            "breathe", "you are", "you deserve", "you can", "you have",
            "present moment", "right now", "it's okay", "be gentle",
            "you're safe", "trust yourself", "let go"
        ]
        
        emphasis_points = []
        script_lower = script_text.lower()
        
        for keyword in emphasis_keywords:
            if keyword in script_lower:
                emphasis_points.append(keyword)
        
        return emphasis_points[:5]  # Limit to top 5

    
    def generate_audio(self, script: VoiceoverScript, voice_params: VoiceParameters) -> AudioContent:
        """
        Generate audio using ElevenLabs API
        
        Args:
            script: Voiceover script to convert to speech
            voice_params: Voice generation parameters
        
        Returns:
            Audio content with MP3 data
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_audio_start",
                    data={
                        "voice_id": voice_params.voice_id,
                        "word_count": len(script.script_text.split())
                    },
                    cycle_id=self.cycle_id
                )
            
            # Call ElevenLabs API
            audio_url, audio_data, duration, metadata = self._call_elevenlabs_api(
                script.script_text,
                voice_params
            )
            
            # Save audio locally
            audio_filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = self.output_dir / "audio" / audio_filename
            
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            audio = AudioContent(
                audio_url=str(audio_path),
                audio_data=audio_data,
                duration_seconds=duration,
                voice_parameters=voice_params,
                elevenlabs_metadata=metadata
            )
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="generate_audio_complete",
                    data={
                        "audio_path": str(audio_path),
                        "duration": duration
                    },
                    cycle_id=self.cycle_id
                )
            
            return audio
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="generation",
                    error=e,
                    context={"action": "generate_audio"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _call_elevenlabs_api(
        self,
        text: str,
        voice_params: VoiceParameters
    ) -> tuple[str, bytes, float, Dict[str, Any]]:
        """
        Call ElevenLabs API to generate audio
        
        Args:
            text: Script text to convert to speech
            voice_params: Voice parameters
        
        Returns:
            Tuple of (audio_url, audio_data, duration, metadata)
        """
        url = f"{self.elevenlabs_base_url}/text-to-speech/{voice_params.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": voice_params.stability,
                "similarity_boost": voice_params.similarity_boost,
                "style": 0.0,  # Neutral style for therapeutic content
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                audio_data = response.content
                
                # Estimate duration (rough calculation: ~150 words per minute for calm speech)
                word_count = len(text.split())
                duration = (word_count / 150) * 60
                
                metadata = {
                    "voice_id": voice_params.voice_id,
                    "stability": voice_params.stability,
                    "similarity_boost": voice_params.similarity_boost,
                    "model": "eleven_monolingual_v1",
                    "generated_at": datetime.now().isoformat()
                }
                
                return "elevenlabs_audio", audio_data, duration, metadata
            else:
                raise Exception(f"ElevenLabs API returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            # Fallback: Create silent audio placeholder
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="elevenlabs_fallback",
                    data={"error": str(e), "using": "silent_audio"},
                    cycle_id=self.cycle_id
                )
            
            # Create a minimal silent MP3 (for demo purposes)
            silent_audio = self._create_silent_audio(30)  # 30 seconds
            
            return "placeholder", silent_audio, 30.0, {
                "fallback": True,
                "reason": str(e)
            }
    
    def _create_silent_audio(self, duration_seconds: int) -> bytes:
        """
        Create silent audio file as fallback
        
        Args:
            duration_seconds: Duration of silent audio
        
        Returns:
            MP3 audio data
        """
        # Minimal MP3 header for silent audio
        # This is a very basic silent MP3 - in production, use proper audio library
        return b'\xff\xfb\x90\x00' * (duration_seconds * 100)  # Rough approximation
    
    def _get_voice_parameters(self, spec: InterventionSpec) -> VoiceParameters:
        """
        Get voice parameters for audio generation
        
        Args:
            spec: Intervention specification
        
        Returns:
            Voice parameters optimized for therapeutic content
        """
        # Default therapeutic voice parameters
        # Using calm, soothing voice settings
        
        # Voice ID selection based on target emotion
        voice_map = {
            "calm": "21m00Tcm4TlvDq8ikWAM",  # Rachel - calm, clear
            "self_acceptance": "EXAVITQu4vr4xnSDxMaL",  # Bella - warm, friendly
            "motivation": "pNInz6obpgDQGcFmaJgB",  # Adam - confident, clear
            "present_awareness": "21m00Tcm4TlvDq8ikWAM",  # Rachel - centered
            "peace": "EXAVITQu4vr4xnSDxMaL"  # Bella - serene
        }
        
        voice_id = voice_map.get(spec.target_emotion, self.default_voice_id)
        
        # Stability: Higher = more consistent, less variation (good for therapeutic)
        # Similarity: Higher = closer to original voice training
        
        return VoiceParameters(
            voice_id=voice_id,
            stability=0.65,  # Balanced consistency
            similarity_boost=0.75,  # Natural sound
            style=spec.target_emotion
        )

    
    def combine_video(self, visual: VisualContent, audio: AudioContent) -> VideoContent:
        """
        Combine visual and audio into video using ffmpeg
        
        Args:
            visual: Visual content (image)
            audio: Audio content (voiceover)
        
        Returns:
            Video content with MP4 file
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="combine_video_start",
                    data={
                        "audio_duration": audio.duration_seconds
                    },
                    cycle_id=self.cycle_id
                )
            
            # Generate output filename
            video_filename = f"mindful_moment_{uuid.uuid4().hex[:8]}.mp4"
            video_path = self.output_dir / "videos" / video_filename
            
            # Use ffmpeg to combine image and audio
            self._run_ffmpeg_composition(
                image_path=visual.image_url,
                audio_path=audio.audio_url,
                output_path=str(video_path),
                duration=audio.duration_seconds
            )
            
            # Read video data
            with open(video_path, "rb") as f:
                video_data = f.read()
            
            # Generate thumbnail (first frame)
            thumbnail_path = str(video_path).replace(".mp4", "_thumb.jpg")
            self._generate_thumbnail(str(video_path), thumbnail_path)
            
            video = VideoContent(
                video_url=str(video_path),
                video_data=video_data,
                duration_seconds=audio.duration_seconds,
                thumbnail_url=thumbnail_path,
                resolution="1920x1080"
            )
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="combine_video_complete",
                    data={
                        "video_path": str(video_path),
                        "duration": audio.duration_seconds,
                        "size_mb": len(video_data) / (1024 * 1024)
                    },
                    cycle_id=self.cycle_id
                )
            
            return video
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="generation",
                    error=e,
                    context={"action": "combine_video"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _run_ffmpeg_composition(
        self,
        image_path: str,
        audio_path: str,
        output_path: str,
        duration: float
    ) -> None:
        """
        Run ffmpeg to combine image and audio into video
        
        Args:
            image_path: Path to image file
            audio_path: Path to audio file
            output_path: Path for output video
            duration: Video duration in seconds
        """
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception("ffmpeg is not installed or not in PATH. Please install ffmpeg.")
        
        # FFmpeg command to create video from image and audio
        # - Loop the image for the duration of the audio
        # - Add subtle zoom effect for visual interest
        # - Add fade in/out transitions
        
        ffmpeg_cmd = [
            "ffmpeg",
            "-loop", "1",  # Loop the image
            "-i", image_path,  # Input image
            "-i", audio_path,  # Input audio
            "-c:v", "libx264",  # Video codec
            "-tune", "stillimage",  # Optimize for still image
            "-c:a", "aac",  # Audio codec
            "-b:a", "192k",  # Audio bitrate
            "-pix_fmt", "yuv420p",  # Pixel format for compatibility
            "-vf", (
                # Video filters: scale to 1920x1080, add subtle zoom, fade in/out
                "scale=1920:1080:force_original_aspect_ratio=increase,"
                "crop=1920:1080,"
                f"zoompan=z='min(zoom+0.0015,1.1)':d={int(duration * 25)}:s=1920x1080,"
                f"fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1"
            ),
            "-shortest",  # End when shortest input ends
            "-t", str(duration),  # Duration
            "-y",  # Overwrite output file
            output_path
        ]
        
        # Run ffmpeg
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"ffmpeg failed: {result.stderr}")
    
    def _generate_thumbnail(self, video_path: str, thumbnail_path: str) -> None:
        """
        Generate thumbnail from video
        
        Args:
            video_path: Path to video file
            thumbnail_path: Path for output thumbnail
        """
        try:
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", "00:00:01",  # Take frame at 1 second
                "-vframes", "1",  # Extract 1 frame
                "-vf", "scale=320:180",  # Thumbnail size
                "-y",
                thumbnail_path
            ]
            
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True, timeout=30)
            
        except Exception as e:
            # Thumbnail generation is optional, log but don't fail
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="thumbnail_generation_failed",
                    data={"error": str(e)},
                    cycle_id=self.cycle_id
                )

    
    def package_intervention(
        self,
        video: VideoContent,
        script: VoiceoverScript,
        visual: VisualContent,
        audio: AudioContent,
        spec: InterventionSpec
    ) -> Intervention:
        """
        Package all components into complete intervention
        
        Args:
            video: Generated video content
            script: Voiceover script
            visual: Visual content
            audio: Audio content
            spec: Original intervention specification
        
        Returns:
            Complete intervention package
        """
        intervention_id = f"intervention_{uuid.uuid4().hex}"
        
        intervention = Intervention(
            intervention_id=intervention_id,
            spec=spec,
            video=video,
            voiceover_script=script,
            audio=audio,
            visual=visual,
            created_at=datetime.now()
        )
        
        # Save intervention metadata
        self._save_intervention_metadata(intervention)
        
        return intervention
    
    def _save_intervention_metadata(self, intervention: Intervention) -> None:
        """
        Save intervention metadata to JSON file
        
        Args:
            intervention: Intervention to save
        """
        try:
            metadata_path = self.output_dir / f"{intervention.intervention_id}_metadata.json"
            
            metadata = {
                "intervention_id": intervention.intervention_id,
                "created_at": intervention.created_at.isoformat(),
                "therapeutic_framework": intervention.spec.therapeutic_framework,
                "target_emotion": intervention.spec.target_emotion,
                "content_theme": intervention.spec.content_theme,
                "video_path": intervention.video.video_url,
                "video_duration": intervention.video.duration_seconds,
                "script_text": intervention.voiceover_script.script_text,
                "voice_parameters": {
                    "voice_id": intervention.audio.voice_parameters.voice_id,
                    "stability": intervention.audio.voice_parameters.stability,
                    "similarity_boost": intervention.audio.voice_parameters.similarity_boost
                }
            }
            
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            # Metadata save is optional, log but don't fail
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="generation",
                    action="metadata_save_failed",
                    data={"error": str(e)},
                    cycle_id=self.cycle_id
                )
    
    def retrieve_style_parameters(self, spec: InterventionSpec) -> StyleParameters:
        """
        Retrieve style parameters from historical data (Yutori integration)
        
        Args:
            spec: Intervention specification
        
        Returns:
            Style parameters (defaults if no history available)
        """
        # TODO: Integrate with Yutori to retrieve historical style parameters
        # For now, return defaults based on spec
        
        style_map = {
            "grounding": StyleParameters(
                tone="calm",
                language_style="simple",
                imagery_style="nature",
                color_palette="earth_tones",
                voice_style="soothing"
            ),
            "self_compassion": StyleParameters(
                tone="warm",
                language_style="poetic",
                imagery_style="nurturing",
                color_palette="warm_earth_tones",
                voice_style="gentle"
            ),
            "mindfulness": StyleParameters(
                tone="centered",
                language_style="simple",
                imagery_style="minimalist",
                color_palette="cool_blues",
                voice_style="meditative"
            ),
            "empowerment": StyleParameters(
                tone="encouraging",
                language_style="direct",
                imagery_style="uplifting",
                color_palette="warm_golds",
                voice_style="confident"
            ),
            "relaxation": StyleParameters(
                tone="serene",
                language_style="gentle",
                imagery_style="peaceful",
                color_palette="soft_pastels",
                voice_style="tranquil"
            )
        }
        
        return style_map.get(spec.content_theme, style_map["relaxation"])
