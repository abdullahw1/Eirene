"""Integration tests for Generation Agent with Strategy Agent"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from src.agents.strategy import StrategyAgent
from src.agents.generation import GenerationAgent
from src.models.stress_signal import StressSignal
from src.utils.trace_logger import TraceLogger

# Load environment variables
load_dotenv()


@pytest.fixture
def trace_logger():
    """Create trace logger for testing"""
    return TraceLogger(traces_dir="./traces")


@pytest.fixture
def strategy_agent(trace_logger):
    """Create Strategy Agent instance"""
    return StrategyAgent(
        yutori_api_key=os.getenv("YUTORI_API_KEY", "test_key"),
        yutori_base_url=os.getenv("YUTORI_BASE_URL", "https://api.yutori.ai"),
        trace_logger=trace_logger,
        cycle_id="integration_test"
    )


@pytest.fixture
def generation_agent(trace_logger):
    """Create Generation Agent instance"""
    return GenerationAgent(
        freepik_api_key=os.getenv("FREEPIK_API_KEY", "test_key"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "test_key"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        output_dir="./test_generated_content",
        trace_logger=trace_logger,
        cycle_id="integration_test"
    )


@pytest.fixture
def sample_stress_signals():
    """Create sample stress signals for testing"""
    return [
        StressSignal(
            source_url="https://reddit.com/r/anxiety",
            signal_type="anxiety",
            community_context="College students expressing finals anxiety",
            severity_indicator=0.85,
            timestamp="2026-01-16T14:30:00Z",
            raw_content="Feeling overwhelmed with finals..."
        ),
        StressSignal(
            source_url="https://reddit.com/r/burnout",
            signal_type="burnout",
            community_context="Tech workers experiencing work burnout",
            severity_indicator=0.90,
            timestamp="2026-01-16T14:30:00Z",
            raw_content="Can't keep up with work demands..."
        ),
        StressSignal(
            source_url="https://reddit.com/r/lonely",
            signal_type="isolation",
            community_context="Remote workers feeling socially isolated",
            severity_indicator=0.75,
            timestamp="2026-01-16T14:30:00Z",
            raw_content="Haven't talked to anyone in days..."
        )
    ]


def test_strategy_to_generation_pipeline(strategy_agent, generation_agent, sample_stress_signals):
    """Test complete Strategy → Generation pipeline"""
    
    for signal in sample_stress_signals:
        # Step 1: Strategy Agent processes stress signal
        therapeutic_context = strategy_agent.query_therapeutic_frameworks(signal)
        
        assert therapeutic_context is not None
        assert therapeutic_context.framework in ["CBT", "DBT"]
        assert len(therapeutic_context.techniques) > 0
        
        # Step 2: Strategy Agent creates intervention spec
        intervention_spec = strategy_agent.map_to_cbt_dbt(therapeutic_context)
        
        assert intervention_spec is not None
        assert intervention_spec.therapeutic_framework in ["CBT", "DBT"]
        assert intervention_spec.target_emotion is not None
        assert intervention_spec.content_theme is not None
        assert len(intervention_spec.visual_guidelines) > 0
        assert len(intervention_spec.text_guidelines) > 0
        
        # Step 3: Generation Agent creates visual
        visual = generation_agent.generate_visual(intervention_spec)
        
        assert visual is not None
        assert visual.image_url is not None
        assert len(visual.image_data) > 0
        assert visual.generation_prompt is not None
        
        # Step 4: Generation Agent creates script
        script = generation_agent.generate_voiceover_script(intervention_spec, visual)
        
        assert script is not None
        assert len(script.script_text) > 0
        assert 30 <= script.duration_seconds <= 60
        assert script.pacing in ["slow", "moderate", "gentle"]
        
        # Step 5: Verify script quality
        script_lower = script.script_text.lower()
        # Should contain therapeutic language
        assert any(word in script_lower for word in [
            "breathe", "moment", "calm", "present", "you are", "you can"
        ])


def test_intervention_spec_to_visual_consistency(generation_agent):
    """Test that visual generation is consistent with intervention spec"""
    
    from src.models.intervention import InterventionSpec
    
    specs = [
        InterventionSpec(
            therapeutic_framework="CBT",
            target_emotion="calm",
            content_theme="grounding",
            visual_guidelines="Natural grounding scene",
            text_guidelines="CBT language",
            therapeutic_intent="Grounding"
        ),
        InterventionSpec(
            therapeutic_framework="DBT",
            target_emotion="self_acceptance",
            content_theme="self_compassion",
            visual_guidelines="Warm nurturing scene",
            text_guidelines="DBT language",
            therapeutic_intent="Self-compassion"
        )
    ]
    
    for spec in specs:
        visual = generation_agent.generate_visual(spec)
        
        # Verify prompt contains theme-related keywords
        prompt_lower = visual.generation_prompt.lower()
        theme_keywords = {
            "grounding": ["ground", "earth", "forest", "stone", "nature"],
            "self_compassion": ["warm", "nurturing", "sunrise", "golden", "compassion"]
        }
        
        keywords = theme_keywords.get(spec.content_theme, [])
        assert any(keyword in prompt_lower for keyword in keywords)


def test_voice_parameters_match_emotion(generation_agent):
    """Test that voice parameters are appropriate for target emotion"""
    
    from src.models.intervention import InterventionSpec
    
    emotions = ["calm", "self_acceptance", "motivation", "present_awareness", "peace"]
    
    for emotion in emotions:
        spec = InterventionSpec(
            therapeutic_framework="CBT",
            target_emotion=emotion,
            content_theme="grounding",
            visual_guidelines="",
            text_guidelines="",
            therapeutic_intent=""
        )
        
        voice_params = generation_agent._get_voice_parameters(spec)
        
        # Verify voice parameters are therapeutic
        assert 0.5 <= voice_params.stability <= 0.8  # Consistent but not robotic
        assert 0.7 <= voice_params.similarity_boost <= 0.85  # Natural sound
        assert voice_params.voice_id is not None
        assert voice_params.style == emotion


def test_script_structure_completeness(generation_agent):
    """Test that generated scripts have proper structure"""
    
    from src.models.intervention import InterventionSpec, VisualContent
    
    spec = InterventionSpec(
        therapeutic_framework="CBT",
        target_emotion="calm",
        content_theme="grounding",
        visual_guidelines="Natural scene",
        text_guidelines="Include opening, exercise, closing",
        therapeutic_intent="Grounding"
    )
    
    visual = VisualContent(
        image_url="test.png",
        image_data=b"test",
        generation_prompt="peaceful scene",
        freepik_metadata={}
    )
    
    script = generation_agent.generate_voiceover_script(spec, visual)
    
    # Verify script has multiple sentences (structure)
    sentences = [s.strip() for s in script.script_text.split('.') if s.strip()]
    assert len(sentences) >= 3  # At least opening, middle, closing
    
    # Verify word count is appropriate for duration
    word_count = len(script.script_text.split())
    expected_words = (script.duration_seconds / 60) * 120  # ~120 words per minute
    assert 0.5 * expected_words <= word_count <= 1.5 * expected_words


def test_style_parameters_by_theme(generation_agent):
    """Test that style parameters are appropriate for each theme"""
    
    from src.models.intervention import InterventionSpec
    
    themes = ["grounding", "self_compassion", "mindfulness", "empowerment", "relaxation"]
    
    for theme in themes:
        spec = InterventionSpec(
            therapeutic_framework="CBT",
            target_emotion="calm",
            content_theme=theme,
            visual_guidelines="",
            text_guidelines="",
            therapeutic_intent=""
        )
        
        style_params = generation_agent.retrieve_style_parameters(spec)
        
        assert style_params.tone is not None
        assert style_params.language_style is not None
        assert style_params.imagery_style is not None
        assert style_params.color_palette is not None
        assert style_params.voice_style is not None
        
        # Verify style is appropriate for theme
        if theme == "grounding":
            assert "earth" in style_params.color_palette.lower() or "nature" in style_params.imagery_style.lower()
        elif theme == "self_compassion":
            assert "warm" in style_params.tone.lower() or "warm" in style_params.color_palette.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
