"""Memory-related data models"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .intervention import StyleParameters, VoiceParameters
from .audit import AuditResult


@dataclass
class ExperienceLog:
    """Historical record of intervention outcomes"""
    
    log_id: str
    intervention_id: str
    stress_signal_type: str
    therapeutic_framework: str
    style_parameters: StyleParameters
    voice_parameters: VoiceParameters
    video_duration: float
    audit_result: AuditResult
    retool_approved: Optional[bool]
    retool_feedback: Optional[str]
    created_at: datetime
