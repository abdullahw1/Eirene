"""Tests for enhanced Strategy Agent functionality"""

import pytest
from datetime import datetime
from src.agents.strategy import StrategyAgent
from src.models.stress_signal import StressSignal


class TestStrategyAgentEnhancements:
    """Test enhanced Strategy Agent features"""
    
    def test_detailed_visual_guidelines(self):
        """Test that visual guidelines are detailed and specific"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="anxiety",
            community_context="Test community",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Visual guidelines should be detailed (>100 chars)
        assert len(spec.visual_guidelines) > 100
        # Should mention specific elements
        assert any(word in spec.visual_guidelines.lower() for word in 
                  ["natural", "earth", "calming", "peaceful", "serene"])
        # Should mention resolution
        assert "1920x1080" in spec.visual_guidelines
        # Should mention what to avoid
        assert "avoid" in spec.visual_guidelines.lower()
    
    def test_detailed_text_guidelines(self):
        """Test that text guidelines include structure and pacing"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="burnout",
            community_context="Test community",
            severity_indicator=0.8,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Text guidelines should be detailed (>200 chars)
        assert len(spec.text_guidelines) > 200
        # Should mention structure
        assert "structure" in spec.text_guidelines.lower() or "opening" in spec.text_guidelines.lower()
        # Should mention duration
        assert "30-60" in spec.text_guidelines
        # Should mention tone
        assert any(word in spec.text_guidelines.lower() for word in 
                  ["warm", "calm", "supportive", "reassuring"])
    
    def test_audio_parameters_included(self):
        """Test that audio parameters are included in text guidelines"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="anxiety",
            community_context="Test community",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Should include audio parameters section
        assert "AUDIO PARAMETERS" in spec.text_guidelines
        # Should mention voice characteristics
        assert "voice" in spec.text_guidelines.lower()
        # Should mention stability and similarity parameters
        assert "stability" in spec.text_guidelines.lower()
        assert "similarity" in spec.text_guidelines.lower()
    
    def test_enhanced_technique_mapping(self):
        """Test that all 8+ signal types map to appropriate techniques"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal_types = [
            "anxiety", "burnout", "isolation", "depression", 
            "stress", "overwhelm", "panic", "grief"
        ]
        
        for signal_type in signal_types:
            signal = StressSignal(
                source_url="https://example.com",
                signal_type=signal_type,
                community_context="Test community",
                severity_indicator=0.7,
                timestamp=datetime.now(),
                raw_content="Test content"
            )
            
            context = agent.query_therapeutic_frameworks(signal)
            
            # Should have framework
            assert context.framework in ["CBT", "DBT"]
            # Should have techniques
            assert len(context.techniques) >= 2
            # Should have clinical rationale
            assert len(context.clinical_rationale) > 50
            # Rationale should mention the signal type
            assert signal_type in context.clinical_rationale.lower()
    
    def test_breathing_exercises_technique(self):
        """Test that breathing exercises get specific guidance"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="anxiety",
            community_context="Test community",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Should include breathing guidance
        assert "breathing" in spec.text_guidelines.lower() or "breathe" in spec.text_guidelines.lower()
        # Should mention pauses for breathing
        if "breathing_exercises" in context.techniques:
            assert "pause" in spec.text_guidelines.lower()
    
    def test_self_compassion_technique(self):
        """Test that self-compassion gets warm, accepting language"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="burnout",
            community_context="Test community",
            severity_indicator=0.8,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Should include self-compassion language
        if "self_compassion" in context.techniques:
            assert any(word in spec.text_guidelines.lower() for word in 
                      ["warm", "accepting", "gentle", "kind", "compassion"])
    
    def test_clinical_rationale_quality(self):
        """Test that clinical rationales are detailed and evidence-based"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="depression",
            community_context="Test community",
            severity_indicator=0.8,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        
        # Rationale should be substantial
        assert len(context.clinical_rationale) > 80
        # Should mention the framework
        assert context.framework in context.clinical_rationale
        # Should mention techniques or their purpose
        assert any(technique in context.clinical_rationale.lower() 
                  for technique in ["cognitive", "behavioral", "mindfulness", "compassion"])
    
    def test_therapeutic_intent_completeness(self):
        """Test that therapeutic intent is comprehensive"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="isolation",
            community_context="Test community",
            severity_indicator=0.7,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Intent should mention framework
        assert spec.therapeutic_framework in spec.therapeutic_intent
        # Intent should mention techniques
        assert any(technique in spec.therapeutic_intent.lower() 
                  for technique in context.techniques)
        # Intent should mention evidence-based support
        assert "evidence-based" in spec.therapeutic_intent.lower()
    
    def test_unknown_signal_type_fallback(self):
        """Test that unknown signal types get reasonable defaults"""
        agent = StrategyAgent(
            yutori_api_key="test_key",
            yutori_base_url="https://api.yutori.ai"
        )
        
        signal = StressSignal(
            source_url="https://example.com",
            signal_type="unknown_type",
            community_context="Test community",
            severity_indicator=0.5,
            timestamp=datetime.now(),
            raw_content="Test content"
        )
        
        context = agent.query_therapeutic_frameworks(signal)
        spec = agent.map_to_cbt_dbt(context)
        
        # Should still produce valid spec
        assert spec.therapeutic_framework in ["CBT", "DBT"]
        assert len(spec.visual_guidelines) > 0
        assert len(spec.text_guidelines) > 0
        assert len(spec.therapeutic_intent) > 0
        # Should have default techniques
        assert len(context.techniques) >= 2
