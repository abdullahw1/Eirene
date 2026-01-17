"""Tests for Monitor and Strategy Agents"""

import pytest
from datetime import datetime
from src.agents.monitor import MonitorAgent
from src.agents.strategy import StrategyAgent
from src.models.stress_signal import StressSignal
from src.utils.trace_logger import TraceLogger


class TestMonitorAgent:
    """Unit tests for Monitor Agent"""
    
    def test_monitor_agent_initialization(self):
        """Test that MonitorAgent initializes correctly"""
        agent = MonitorAgent(agentql_api_key="test_key")
        assert agent.agentql_api_key == "test_key"
        assert agent.mcp_process is None
    
    def test_connect_tinyfish_mcp_success(self):
        """Test successful MCP connection"""
        agent = MonitorAgent(agentql_api_key="test_key")
        result = agent.connect_tinyfish_mcp()
        assert result is True
    
    def test_connect_tinyfish_mcp_no_key(self):
        """Test MCP connection fails without API key"""
        agent = MonitorAgent(agentql_api_key="")
        with pytest.raises(ValueError):
            agent.connect_tinyfish_mcp()
    
    def test_extract_signal_metadata(self):
        """Test extracting structured signal from raw data"""
        agent = MonitorAgent(agentql_api_key="test_key")
        
        raw_data = {
            "url": "https://reddit.com/r/anxiety/post123",
            "content": "I'm feeling very anxious and worried about everything",
            "timestamp": datetime.now()
        }
        
        signal = agent.extract_signal_metadata(raw_data)
        
        assert isinstance(signal, StressSignal)
        assert signal.source_url == raw_data["url"]
        assert signal.signal_type == "anxiety"
        assert 0.0 <= signal.severity_indicator <= 1.0
        assert "Reddit community" in signal.community_context
        assert signal.raw_content == raw_data["content"]
    
    def test_classify_signal_type_anxiety(self):
        """Test anxiety signal classification"""
        agent = MonitorAgent(agentql_api_key="test_key")
        signal_type = agent._classify_signal_type("I'm feeling very anxious and worried")
        assert signal_type == "anxiety"
    
    def test_classify_signal_type_burnout(self):
        """Test burnout signal classification"""
        agent = MonitorAgent(agentql_api_key="test_key")
        signal_type = agent._classify_signal_type("I'm completely burned out and exhausted")
        assert signal_type == "burnout"
    
    def test_classify_signal_type_isolation(self):
        """Test isolation signal classification"""
        agent = MonitorAgent(agentql_api_key="test_key")
        signal_type = agent._classify_signal_type("I feel so lonely and isolated")
        assert signal_type == "isolation"
    
    def test_calculate_severity(self):
        """Test severity calculation"""
        agent = MonitorAgent(agentql_api_key="test_key")
        
        # Low severity
        severity_low = agent._calculate_severity("I'm a bit stressed")
        assert 0.0 <= severity_low <= 1.0
        
        # High severity
        severity_high = agent._calculate_severity("I'm in crisis and can't cope, feeling desperate")
        assert severity_high > severity_low
        assert severity_high <= 1.0


class TestStrategyAgent:
    """Unit tests for Strategy Agent"""
    
    def test_strategy_agent_initialization(self):
        """Test that StrategyAgent initializes correctly"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        assert agent.yutori_api_key == "test_key"
        assert agent.yutori_base_url == "https://api.yutori.ai"
    
    def test_query_therapeutic_frameworks_anxiety(self):
        """Test querying frameworks for anxiety signal"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="anxiety",
            community_context="Reddit community: r/anxiety",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="I'm feeling anxious"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        
        assert context.framework in ["CBT", "DBT"]
        assert len(context.techniques) > 0
        assert context.clinical_rationale != ""
        assert len(context.yutori_references) > 0
    
    def test_map_to_cbt_dbt(self):
        """Test mapping therapeutic context to intervention spec"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="anxiety",
            community_context="Reddit community: r/anxiety",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="I'm feeling anxious"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        assert spec.therapeutic_framework in ["CBT", "DBT"]
        assert spec.target_emotion != ""
        assert spec.content_theme != ""
        assert spec.visual_guidelines != ""
        assert spec.text_guidelines != ""
        assert spec.therapeutic_intent != ""
    
    def test_intervention_spec_completeness(self):
        """Test that intervention spec contains all required fields"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="burnout",
            community_context="General online community",
            severity_indicator=0.8,
            timestamp=datetime.now(),
            raw_content="I'm burned out"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Verify all fields are non-empty
        assert spec.therapeutic_framework
        assert spec.target_emotion
        assert spec.content_theme
        assert spec.visual_guidelines
        assert spec.text_guidelines
        assert spec.therapeutic_intent


class TestMonitorStrategyIntegration:
    """Integration tests for Monitor and Strategy agents working together"""
    
    def test_monitor_to_strategy_pipeline(self):
        """Test complete flow from Monitor to Strategy agent"""
        # Initialize agents
        monitor = MonitorAgent(agentql_api_key="test_key")
        strategy = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        # Monitor extracts signal
        raw_data = {
            "url": "https://reddit.com/r/anxiety/post123",
            "content": "I'm feeling very anxious and can't sleep",
            "timestamp": datetime.now()
        }
        
        signal = monitor.extract_signal_metadata(raw_data)
        
        # Strategy processes signal
        context = strategy.query_therapeutic_frameworks(signal)
        spec = strategy.map_to_cbt_dbt(context)
        
        # Verify pipeline output
        assert signal.signal_type == "anxiety"
        assert spec.therapeutic_framework in ["CBT", "DBT"]
        assert spec.content_theme != ""
