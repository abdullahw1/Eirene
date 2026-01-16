"""Unit tests for Manager Agent"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from src.agents.manager import ManagerAgent, CycleResult, RecoveryAction
from src.models.config import SystemConfig
from src.models.pipeline import PipelineStatus, AgentType
from src.models.stress_signal import StressSignal
from src.models.intervention import InterventionSpec


class TestManagerAgent:
    """Test suite for Manager Agent"""
    
    @pytest.fixture
    def temp_traces_dir(self):
        """Create a temporary directory for traces"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_config(self, temp_traces_dir):
        """Create a test configuration"""
        return SystemConfig(
            agentql_api_key="test_key",
            freepik_api_key="test_key",
            elevenlabs_api_key="test_key",
            modulate_api_key="test_key",
            yutori_api_key="test_key",
            yutori_base_url="https://test.yutori.ai",
            retool_api_key="test_key",
            retool_webhook_url="https://test.retool.com",
            traces_directory=temp_traces_dir,
            enable_retool_review=False,
            audit_alignment_threshold=0.75,
            modulate_confidence_threshold=0.7,
            max_regeneration_attempts=3,
            cycle_interval_seconds=300,
            video_duration_min=30,
            video_duration_max=60
        )
    
    def test_manager_initialization(self, test_config):
        """Test that Manager Agent initializes correctly"""
        manager = ManagerAgent(test_config)
        
        assert manager.config == test_config
        assert manager.trace_logger is not None
        assert manager.current_state is None
        assert manager.consecutive_failures == 0
    
    def test_initialize_pipeline(self, test_config):
        """Test pipeline initialization"""
        manager = ManagerAgent(test_config)
        state = manager.initialize_pipeline()
        
        # Verify state is created correctly
        assert state is not None
        assert state.cycle_id.startswith("cycle_")
        assert state.current_agent == AgentType.MONITOR
        assert state.status == PipelineStatus.RUNNING
        assert state.started_at is not None
        assert state.completed_at is None
        
        # Verify all fields are initialized
        assert state.stress_signal is None
        assert state.intervention_spec is None
        assert state.intervention is None
        assert state.audit_result is None
        assert state.experience_log_id is None
        
        # Verify trace directory was created
        cycle_dir = Path(test_config.traces_directory) / state.cycle_id
        assert cycle_dir.exists()
        
        # Verify initialization trace was logged
        traces = manager.trace_logger.get_cycle_traces(state.cycle_id)
        assert len(traces) > 0
        assert any(t["action"] == "initialize_complete" for t in traces)
    
    def test_execute_cycle_without_initialization(self, test_config):
        """Test that execute_cycle fails if pipeline not initialized"""
        manager = ManagerAgent(test_config)
        
        with pytest.raises(RuntimeError, match="Pipeline not initialized"):
            manager.execute_cycle()
    
    def test_execute_cycle_success(self, test_config):
        """Test successful cycle execution"""
        manager = ManagerAgent(test_config)
        manager.initialize_pipeline()
        
        result = manager.execute_cycle()
        
        # Verify cycle completed successfully
        assert result == CycleResult.SUCCESS
        assert manager.current_state.status == PipelineStatus.COMPLETED
        assert manager.current_state.completed_at is not None
        assert manager.consecutive_failures == 0
        
        # Verify all stages were logged
        traces = manager.trace_logger.get_cycle_traces(manager.current_state.cycle_id)
        stage_traces = [t for t in traces if t["action"] == "stage_placeholder"]
        assert len(stage_traces) == 5  # All 5 stages
    
    def test_route_to_next_agent(self, test_config):
        """Test routing data between agents"""
        manager = ManagerAgent(test_config)
        manager.initialize_pipeline()
        
        # Create test data
        test_signal = StressSignal(
            source_url="https://test.com",
            signal_type="anxiety",
            community_context="test context",
            severity_indicator=0.8,
            timestamp=datetime.now(timezone.utc),
            raw_content="test content"
        )
        
        # Route from Monitor to Strategy
        manager.route_to_next_agent(test_signal, AgentType.MONITOR)
        
        # Verify state was updated
        assert manager.current_state.stress_signal == test_signal
        assert manager.current_state.current_agent == AgentType.STRATEGY
        
        # Verify routing was logged
        traces = manager.trace_logger.get_cycle_traces(manager.current_state.cycle_id)
        route_traces = [t for t in traces if t["action"] == "route_data"]
        assert len(route_traces) == 1
        assert route_traces[0]["data"]["from_agent"] == "monitor"
        assert route_traces[0]["data"]["to_agent"] == "strategy"
    
    def test_handle_agent_failure_retry(self, test_config):
        """Test agent failure handling with retry"""
        manager = ManagerAgent(test_config)
        manager.initialize_pipeline()
        
        error = Exception("Test error")
        action = manager.handle_agent_failure(AgentType.MONITOR, error, retry_count=0)
        
        # Should retry on first failure
        assert action == RecoveryAction.RETRY
        
        # Verify error was logged
        errors = manager.trace_logger.get_cycle_errors(manager.current_state.cycle_id)
        assert len(errors) == 1
        assert errors[0]["agent"] == "monitor"
    
    def test_handle_agent_failure_skip(self, test_config):
        """Test agent failure handling with skip after max retries"""
        manager = ManagerAgent(test_config)
        manager.initialize_pipeline()
        
        error = Exception("Test error")
        action = manager.handle_agent_failure(AgentType.MONITOR, error, retry_count=3)
        
        # Should skip after max retries
        assert action == RecoveryAction.SKIP
        assert manager.consecutive_failures == 1
    
    def test_handle_agent_failure_circuit_breaker(self, test_config):
        """Test circuit breaker after consecutive failures"""
        manager = ManagerAgent(test_config)
        manager.initialize_pipeline()
        
        # Simulate multiple consecutive failures
        manager.consecutive_failures = 4
        
        error = Exception("Test error")
        action = manager.handle_agent_failure(AgentType.MONITOR, error, retry_count=3)
        
        # Should terminate due to circuit breaker
        assert action == RecoveryAction.TERMINATE
        assert manager.consecutive_failures == 5
    
    def test_route_to_next_agent_without_initialization(self, test_config):
        """Test that routing fails if pipeline not initialized"""
        manager = ManagerAgent(test_config)
        
        with pytest.raises(RuntimeError, match="Pipeline not initialized"):
            manager.route_to_next_agent(None, AgentType.MONITOR)
    
    def test_invalid_config_initialization(self, temp_traces_dir):
        """Test that initialization fails with invalid config"""
        invalid_config = SystemConfig(
            agentql_api_key="",  # Invalid: empty key
            freepik_api_key="",
            elevenlabs_api_key="",
            modulate_api_key="",
            yutori_api_key="",
            yutori_base_url="https://test.yutori.ai",
            retool_api_key="",
            retool_webhook_url="",
            traces_directory=temp_traces_dir,
            enable_retool_review=False,
            audit_alignment_threshold=0.75,
            modulate_confidence_threshold=0.7,
            max_regeneration_attempts=3,
            cycle_interval_seconds=300,
            video_duration_min=30,
            video_duration_max=60
        )
        
        manager = ManagerAgent(invalid_config)
        
        with pytest.raises(RuntimeError, match="Invalid system configuration"):
            manager.initialize_pipeline()
