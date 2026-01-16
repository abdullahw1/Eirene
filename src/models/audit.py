"""Audit-related data models"""

from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    """Visual content validation result"""
    
    visual_appropriate: bool
    matches_guidelines: bool
    quality_score: float  # 0.0 to 1.0
    issues: List[str]


@dataclass
class ScriptValidationResult:
    """Voiceover script validation result"""
    
    script_appropriate: bool
    therapeutic_alignment: bool
    duration_acceptable: bool  # 30-60 seconds
    issues: List[str]


@dataclass
class EmotionalValidationResult:
    """Emotional tone validation result from Modulate"""
    
    emotion_matches_intent: bool
    modulate_confidence: float  # 0.0 to 1.0
    detected_emotions: List[str]
    issues: List[str]


@dataclass
class AuditResult:
    """Complete audit result for an intervention"""
    
    passed: bool
    alignment_score: float  # 0.0 to 1.0
    validation_result: ValidationResult
    script_validation: ScriptValidationResult
    emotional_validation: EmotionalValidationResult
    reason: str  # Explanation for pass/fail
