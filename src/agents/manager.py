"""Manager Agent - Orchestrates the autonomous empathy response pipeline"""

import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from enum import Enum

from ..models.pipeline import PipelineState, PipelineStatus, AgentType
from ..models.stress_signal import StressSignal
from ..models.intervention import InterventionSpec, Intervention
from ..models.audit import AuditResult
from ..models.config import SystemConfig
from ..utils.trace_logger import TraceLogger


class RecoveryAction(Enum):
    """Recovery actions for agent failures"""
    RETRY = "retry"
    SKIP = "skip"
    TERMINATE = "terminate"


class CycleResult(Enum):
    """Result of a pipeline cycle execution"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class ManagerAgent:
    """
    Manager Agent coordinates all sub-agents in the empathy response pipeline.
    
    Responsibilities:
    - Initialize and coordinate all sub-agents
    - Route data between agents in the pipeline
    - Handle error recovery and retry logic
    - Maintain execution state across cycles
    - Log all actions via TraceLogger
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize the Manager Agent
        
        Args:
            config: System configuration
        """
        self.config = config
        self.trace_logger = TraceLogger(config.traces_directory)
        self.current_state: Optional[PipelineState] = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        
        # Agent instances (to be initialized)
        self.monitor_agent = None
        self.strategy_agent = None
        self.generation_agent = None
        self.audit_agent = None
        self.memory_agent = None
    
    def initialize_pipeline(self) -> PipelineState:
        """
        Initialize the pipeline and all sub-agents
        
        Returns:
            Initial pipeline state
            
        Raises:
            RuntimeError: If initialization fails
        """
        cycle_id = self._generate_cycle_id()
        
        try:
            # Create cycle directory for traces
            self.trace_logger.create_cycle_directory(cycle_id)
            
            # Log initialization start
            self.trace_logger.log_agent_action(
                agent="manager",
                action="initialize_start",
                data={"cycle_id": cycle_id},
                cycle_id=cycle_id,
                status="in_progress"
            )
            
            # Validate configuration
            if not self.config.validate():
                raise RuntimeError("Invalid system configuration")
            
            # Initialize sub-agents in sequence
            # Note: Actual agent implementations will be added in later tasks
            # For now, we set placeholders to None
            self._initialize_monitor_agent(cycle_id)
            self._initialize_strategy_agent(cycle_id)
            self._initialize_generation_agent(cycle_id)
            self._initialize_audit_agent(cycle_id)
            self._initialize_memory_agent(cycle_id)
            
            # Create initial pipeline state
            initial_state = PipelineState(
                cycle_id=cycle_id,
                current_agent=AgentType.MONITOR,
                stress_signal=None,
                intervention_spec=None,
                intervention=None,
                audit_result=None,
                experience_log_id=None,
                status=PipelineStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
                completed_at=None
            )
            
            self.current_state = initial_state
            
            # Log successful initialization
            self.trace_logger.log_agent_action(
                agent="manager",
                action="initialize_complete",
                data={
                    "agents_initialized": [
                        "monitor", "strategy", "generation", "audit", "memory"
                    ],
                    "config_valid": True
                },
                cycle_id=cycle_id,
                status="success"
            )
            
            return initial_state
            
        except Exception as e:
            # Log initialization failure
            self.trace_logger.log_error(
                agent="manager",
                error=e,
                context={"action": "initialize_pipeline", "cycle_id": cycle_id},
                cycle_id=cycle_id
            )
            raise RuntimeError(f"Pipeline initialization failed: {str(e)}") from e
    
    def execute_cycle(self) -> CycleResult:
        """
        Execute one complete pipeline cycle: Monitor → Strategy → Generation → Audit → Memory
        
        Returns:
            Result of the cycle execution
        """
        if self.current_state is None:
            raise RuntimeError("Pipeline not initialized. Call initialize_pipeline() first.")
        
        cycle_id = self.current_state.cycle_id
        
        try:
            self.trace_logger.log_agent_action(
                agent="manager",
                action="cycle_start",
                data={"cycle_id": cycle_id},
                cycle_id=cycle_id,
                status="in_progress"
            )
            
            # Execute pipeline stages in sequence
            # Stage 1: Monitor Agent
            if not self._execute_monitor_stage(cycle_id):
                return self._handle_cycle_failure(cycle_id, "monitor")
            
            # Stage 2: Strategy Agent
            if not self._execute_strategy_stage(cycle_id):
                return self._handle_cycle_failure(cycle_id, "strategy")
            
            # Stage 3: Generation Agent
            if not self._execute_generation_stage(cycle_id):
                return self._handle_cycle_failure(cycle_id, "generation")
            
            # Stage 4: Audit Agent
            if not self._execute_audit_stage(cycle_id):
                return self._handle_cycle_failure(cycle_id, "audit")
            
            # Stage 5: Memory Agent
            if not self._execute_memory_stage(cycle_id):
                return self._handle_cycle_failure(cycle_id, "memory")
            
            # Mark cycle as completed
            self.current_state.status = PipelineStatus.COMPLETED
            self.current_state.completed_at = datetime.now(timezone.utc)
            
            # Reset consecutive failures on success
            self.consecutive_failures = 0
            
            self.trace_logger.log_agent_action(
                agent="manager",
                action="cycle_complete",
                data={
                    "cycle_id": cycle_id,
                    "duration_seconds": (
                        self.current_state.completed_at - self.current_state.started_at
                    ).total_seconds()
                },
                cycle_id=cycle_id,
                status="success"
            )
            
            return CycleResult.SUCCESS
            
        except Exception as e:
            self.trace_logger.log_error(
                agent="manager",
                error=e,
                context={"action": "execute_cycle", "cycle_id": cycle_id},
                cycle_id=cycle_id
            )
            return self._handle_cycle_failure(cycle_id, "manager")
    
    def route_to_next_agent(
        self,
        data: Any,
        current_agent: AgentType
    ) -> None:
        """
        Route output data to the next agent in the pipeline
        
        Args:
            data: Output data from current agent
            current_agent: The agent that just completed
        """
        if self.current_state is None:
            raise RuntimeError("Pipeline not initialized")
        
        cycle_id = self.current_state.cycle_id
        
        # Determine next agent and update state
        routing_map = {
            AgentType.MONITOR: (AgentType.STRATEGY, "stress_signal"),
            AgentType.STRATEGY: (AgentType.GENERATION, "intervention_spec"),
            AgentType.GENERATION: (AgentType.AUDIT, "intervention"),
            AgentType.AUDIT: (AgentType.MEMORY, "audit_result"),
            AgentType.MEMORY: (None, "experience_log_id")
        }
        
        if current_agent not in routing_map:
            raise ValueError(f"Unknown agent type: {current_agent}")
        
        next_agent, data_field = routing_map[current_agent]
        
        # Update pipeline state with the data
        setattr(self.current_state, data_field, data)
        
        # Log routing action
        self.trace_logger.log_agent_action(
            agent="manager",
            action="route_data",
            data={
                "from_agent": current_agent.value,
                "to_agent": next_agent.value if next_agent else "complete",
                "data_field": data_field,
                "data_present": data is not None
            },
            cycle_id=cycle_id,
            status="success"
        )
        
        # Update current agent
        if next_agent:
            self.current_state.current_agent = next_agent
    
    def handle_agent_failure(
        self,
        agent: AgentType,
        error: Exception,
        retry_count: int = 0
    ) -> RecoveryAction:
        """
        Handle agent failure with retry logic or graceful termination
        
        Args:
            agent: The agent that failed
            error: The exception that was raised
            retry_count: Number of retries attempted so far
            
        Returns:
            Recovery action to take
        """
        if self.current_state is None:
            return RecoveryAction.TERMINATE
        
        cycle_id = self.current_state.cycle_id
        max_retries = 3
        
        # Log the failure
        self.trace_logger.log_error(
            agent=agent.value,
            error=error,
            context={
                "retry_count": retry_count,
                "max_retries": max_retries
            },
            cycle_id=cycle_id
        )
        
        # Determine recovery action
        if retry_count < max_retries:
            # Retry with exponential backoff
            backoff_seconds = 2 ** retry_count
            
            self.trace_logger.log_agent_action(
                agent="manager",
                action="retry_scheduled",
                data={
                    "failed_agent": agent.value,
                    "retry_count": retry_count + 1,
                    "backoff_seconds": backoff_seconds
                },
                cycle_id=cycle_id,
                status="in_progress"
            )
            
            time.sleep(backoff_seconds)
            return RecoveryAction.RETRY
        else:
            # Max retries exceeded
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.max_consecutive_failures:
                # Circuit breaker: too many consecutive failures
                self.trace_logger.log_agent_action(
                    agent="manager",
                    action="circuit_breaker_triggered",
                    data={
                        "consecutive_failures": self.consecutive_failures,
                        "max_failures": self.max_consecutive_failures
                    },
                    cycle_id=cycle_id,
                    status="failed"
                )
                return RecoveryAction.TERMINATE
            else:
                # Skip this cycle and try again later
                self.trace_logger.log_agent_action(
                    agent="manager",
                    action="cycle_skipped",
                    data={
                        "failed_agent": agent.value,
                        "consecutive_failures": self.consecutive_failures
                    },
                    cycle_id=cycle_id,
                    status="failed"
                )
                return RecoveryAction.SKIP
    
    def _generate_cycle_id(self) -> str:
        """Generate a unique cycle ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"cycle_{timestamp}"
    
    def _initialize_monitor_agent(self, cycle_id: str) -> None:
        """Initialize Monitor Agent (placeholder for now)"""
        # TODO: Implement in task 3.1
        self.monitor_agent = None
        self.trace_logger.log_agent_action(
            agent="manager",
            action="agent_initialized",
            data={"agent_type": "monitor"},
            cycle_id=cycle_id,
            status="success"
        )
    
    def _initialize_strategy_agent(self, cycle_id: str) -> None:
        """Initialize Strategy Agent (placeholder for now)"""
        # TODO: Implement in task 3.2
        self.strategy_agent = None
        self.trace_logger.log_agent_action(
            agent="manager",
            action="agent_initialized",
            data={"agent_type": "strategy"},
            cycle_id=cycle_id,
            status="success"
        )
    
    def _initialize_generation_agent(self, cycle_id: str) -> None:
        """Initialize Generation Agent (placeholder for now)"""
        # TODO: Implement in task 4.1
        self.generation_agent = None
        self.trace_logger.log_agent_action(
            agent="manager",
            action="agent_initialized",
            data={"agent_type": "generation"},
            cycle_id=cycle_id,
            status="success"
        )
    
    def _initialize_audit_agent(self, cycle_id: str) -> None:
        """Initialize Audit Agent (placeholder for now)"""
        # TODO: Implement in task 5.1
        self.audit_agent = None
        self.trace_logger.log_agent_action(
            agent="manager",
            action="agent_initialized",
            data={"agent_type": "audit"},
            cycle_id=cycle_id,
            status="success"
        )
    
    def _initialize_memory_agent(self, cycle_id: str) -> None:
        """Initialize Memory Agent (placeholder for now)"""
        # TODO: Implement in task 6.1
        self.memory_agent = None
        self.trace_logger.log_agent_action(
            agent="manager",
            action="agent_initialized",
            data={"agent_type": "memory"},
            cycle_id=cycle_id,
            status="success"
        )
    
    def _execute_monitor_stage(self, cycle_id: str) -> bool:
        """Execute Monitor Agent stage (placeholder for now)"""
        # TODO: Implement actual monitor agent execution in task 3.1
        self.trace_logger.log_agent_action(
            agent="manager",
            action="stage_placeholder",
            data={"stage": "monitor", "message": "Monitor agent not yet implemented"},
            cycle_id=cycle_id,
            status="success"
        )
        return True
    
    def _execute_strategy_stage(self, cycle_id: str) -> bool:
        """Execute Strategy Agent stage (placeholder for now)"""
        # TODO: Implement actual strategy agent execution in task 3.2
        self.trace_logger.log_agent_action(
            agent="manager",
            action="stage_placeholder",
            data={"stage": "strategy", "message": "Strategy agent not yet implemented"},
            cycle_id=cycle_id,
            status="success"
        )
        return True
    
    def _execute_generation_stage(self, cycle_id: str) -> bool:
        """Execute Generation Agent stage (placeholder for now)"""
        # TODO: Implement actual generation agent execution in task 4.1
        self.trace_logger.log_agent_action(
            agent="manager",
            action="stage_placeholder",
            data={"stage": "generation", "message": "Generation agent not yet implemented"},
            cycle_id=cycle_id,
            status="success"
        )
        return True
    
    def _execute_audit_stage(self, cycle_id: str) -> bool:
        """Execute Audit Agent stage (placeholder for now)"""
        # TODO: Implement actual audit agent execution in task 5.1
        self.trace_logger.log_agent_action(
            agent="manager",
            action="stage_placeholder",
            data={"stage": "audit", "message": "Audit agent not yet implemented"},
            cycle_id=cycle_id,
            status="success"
        )
        return True
    
    def _execute_memory_stage(self, cycle_id: str) -> bool:
        """Execute Memory Agent stage (placeholder for now)"""
        # TODO: Implement actual memory agent execution in task 6.1
        self.trace_logger.log_agent_action(
            agent="manager",
            action="stage_placeholder",
            data={"stage": "memory", "message": "Memory agent not yet implemented"},
            cycle_id=cycle_id,
            status="success"
        )
        return True
    
    def _handle_cycle_failure(self, cycle_id: str, failed_stage: str) -> CycleResult:
        """Handle a cycle failure"""
        self.current_state.status = PipelineStatus.FAILED
        self.current_state.completed_at = datetime.now(timezone.utc)
        self.consecutive_failures += 1
        
        self.trace_logger.log_agent_action(
            agent="manager",
            action="cycle_failed",
            data={
                "failed_stage": failed_stage,
                "consecutive_failures": self.consecutive_failures
            },
            cycle_id=cycle_id,
            status="failed"
        )
        
        return CycleResult.FAILED
