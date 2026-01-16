"""Stress signal data model"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class StressSignal:
    """Community-level stress indicator detected from web sources"""
    
    source_url: str
    signal_type: str  # e.g., "anxiety", "burnout", "isolation"
    community_context: str
    severity_indicator: float  # 0.0 to 1.0
    timestamp: datetime
    raw_content: str
