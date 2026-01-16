"""System configuration model"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path


@dataclass
class SystemConfig:
    """System-wide configuration"""
    
    # API Keys
    agentql_api_key: str
    freepik_api_key: str
    elevenlabs_api_key: str
    modulate_api_key: str
    yutori_api_key: str
    yutori_base_url: str
    retool_api_key: str
    retool_webhook_url: str
    
    # System Settings
    traces_directory: str
    enable_retool_review: bool
    audit_alignment_threshold: float
    modulate_confidence_threshold: float
    max_regeneration_attempts: int
    cycle_interval_seconds: int
    video_duration_min: int  # 30 seconds
    video_duration_max: int  # 60 seconds
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "SystemConfig":
        """Load configuration from environment variables or .env file"""
        if env_file:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        return cls(
            # API Keys
            agentql_api_key=os.getenv("AGENTQL_API_KEY", ""),
            freepik_api_key=os.getenv("FREEPIK_API_KEY", ""),
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
            modulate_api_key=os.getenv("MODULATE_API_KEY", ""),
            yutori_api_key=os.getenv("YUTORI_API_KEY", ""),
            yutori_base_url=os.getenv("YUTORI_BASE_URL", "https://api.yutori.ai"),
            retool_api_key=os.getenv("RETOOL_API_KEY", ""),
            retool_webhook_url=os.getenv("RETOOL_WEBHOOK_URL", ""),
            
            # System Settings
            traces_directory=os.getenv("TRACES_DIRECTORY", "./traces"),
            enable_retool_review=os.getenv("ENABLE_RETOOL_REVIEW", "false").lower() == "true",
            audit_alignment_threshold=float(os.getenv("AUDIT_ALIGNMENT_THRESHOLD", "0.75")),
            modulate_confidence_threshold=float(os.getenv("MODULATE_CONFIDENCE_THRESHOLD", "0.7")),
            max_regeneration_attempts=int(os.getenv("MAX_REGENERATION_ATTEMPTS", "3")),
            cycle_interval_seconds=int(os.getenv("CYCLE_INTERVAL_SECONDS", "300")),
            video_duration_min=int(os.getenv("VIDEO_DURATION_MIN", "30")),
            video_duration_max=int(os.getenv("VIDEO_DURATION_MAX", "60")),
        )
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        required_keys = [
            self.agentql_api_key,
            self.freepik_api_key,
            self.elevenlabs_api_key,
            self.modulate_api_key,
            self.yutori_api_key,
        ]
        
        if not all(required_keys):
            return False
        
        # Validate thresholds
        if not (0.0 <= self.audit_alignment_threshold <= 1.0):
            return False
        if not (0.0 <= self.modulate_confidence_threshold <= 1.0):
            return False
        
        # Validate video duration
        if self.video_duration_min >= self.video_duration_max:
            return False
        
        return True
