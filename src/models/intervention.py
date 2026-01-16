"""Intervention-related data models"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class InterventionSpec:
    """Specification for generating an intervention"""
    
    therapeutic_framework: str  # "CBT" or "DBT"
    target_emotion: str
    content_theme: str  # e.g., "grounding", "self-compassion"
    visual_guidelines: str
    text_guidelines: str
    therapeutic_intent: str  # Used by Audit Agent


@dataclass
class StyleParameters:
    """Style parameters for content generation"""
    
    tone: str  # e.g., "calm", "warm", "reassuring"
    language_style: str  # e.g., "simple", "poetic", "direct"
    imagery_style: str  # e.g., "nature", "abstract", "minimalist"
    color_palette: str  # e.g., "cool_blues", "warm_earth_tones"
    voice_style: str  # e.g., "soothing", "gentle", "confident"


@dataclass
class VisualContent:
    """Generated visual content from Freepik"""
    
    image_url: str
    image_data: bytes
    generation_prompt: str
    freepik_metadata: Dict[str, Any]


@dataclass
class VoiceoverScript:
    """Therapeutic voiceover script"""
    
    script_text: str
    duration_seconds: int  # Target 30-60 seconds
    pacing: str  # e.g., "slow", "moderate", "gentle"
    emphasis_points: List[str]


@dataclass
class VoiceParameters:
    """ElevenLabs voice generation parameters"""
    
    voice_id: str  # ElevenLabs voice ID
    stability: float  # 0.0 to 1.0
    similarity_boost: float  # 0.0 to 1.0
    style: str  # From StyleParameters.voice_style


@dataclass
class AudioContent:
    """Generated audio content from ElevenLabs"""
    
    audio_url: str
    audio_data: bytes
    duration_seconds: float
    voice_parameters: VoiceParameters
    elevenlabs_metadata: Dict[str, Any]


@dataclass
class VideoContent:
    """Composed video content"""
    
    video_url: str
    video_data: bytes
    duration_seconds: float
    thumbnail_url: str
    resolution: str  # e.g., "1920x1080"


@dataclass
class Intervention:
    """Complete intervention package"""
    
    intervention_id: str
    spec: InterventionSpec
    video: VideoContent
    voiceover_script: VoiceoverScript
    audio: AudioContent
    visual: VisualContent
    created_at: datetime
