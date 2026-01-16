"""Pipeline state and orchestration models"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .stress_signal import StressSignal
from .intervention import InterventionSpec, Intervention
from .audit import AuditResult


class PipelineStatus(Enum):
    """Pipeline execution status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    """Agent types in the pipeline"""
    MONITOR = "monitor"
    STRATEGY = "strategy"
    GENERATION = "generation"
    AUDIT = "audit"
    MEMORY = "memory"


@dataclass
class PipelineState:
    """Current state of the pipeline execution"""
    
    cycle_id: str
    current_agent: AgentType
    stress_signal: Optional[StressSignal]
    intervention_spec: Optional[InterventionSpec]
    intervention: Optional[Intervention]
    audit_result: Optional[AuditResult]
    experience_log_id: Optional[str]
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime]
