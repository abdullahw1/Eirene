"""Tests for Generation Agent"""

import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from src.agents.generation import GenerationAgent
from src.models.intervention import InterventionSpec
from src.utils.trace_logger import TraceLogger

# Load environment variables
load_dotenv()


@pytest.fixture
def generation_agent():
    """Create a Generation Agent instance for testing"""
    freepik_key = os.getenv("FREEPIK_API_KEY", "test_key")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "test_key")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    trace_logger = TraceLogger(traces_dir="./traces")
    
    return GenerationAgent(
        freepik_api_key=freepik_key,
        elevenlabs_api_key=elevenlabs_key,
        openai_api_key=openai_key,
        output_dir="./test_generated_content",
        trace_logger=trace_logger,
        cycle_id="test_cycle"
    )


@pytest.fixture
def sample_intervention_spec():
    """Create a sample intervention specification"""
    return InterventionSpec(
        therapeutic_framework="CBT",
        target_emotion="calm",
        content_theme="grounding",
        visual_guidelines="Natural grounding scene with forest floor, earth tones, soft lighting",
        text_guidelines="Use CBT-based language. Include breathing exercises. Structure: Opening, exercise, closing.",
        therapeutic_intent="Apply CBT framework using grounding techniques to provide support"
    )


def test_generation_agent_initialization(generation_agent):
    """Test that Generation Agent initializes correctly"""
    assert generation_agent is not None
    assert generation_agent.output_dir.exists()
    assert (generation_agent.output_dir / "images").exists()
    assert (generation_agent.output_dir / "audio").exists()
    assert (generation_agent.output_dir / "videos").exists()


def test_build_visual_prompt(generation_agent, sample_intervention_spec):
    """Test visual prompt building"""
    prompt = generation_agent._build_visual_prompt(sample_intervention_spec)
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "grounding" in prompt.lower() or "forest" in prompt.lower()
    assert "1920x1080" in prompt or "high resolution" in prompt.lower()


def test_generate_template_script(generation_agent, sample_intervention_spec):
    """Test template-based script generation"""
    script = generation_agent._generate_template_script(sample_intervention_spec)
    
    assert isinstance(script, str)
    assert len(script) > 50  # Should be substantial
    assert len(script.split()) >= 30  # At least 30 words
    
    # Check for therapeutic language
    script_lower = script.lower()
    assert any(word in script_lower for word in ["breathe", "moment", "calm", "ground", "present"])


def test_determine_pacing(generation_agent, sample_intervention_spec):
    """Test pacing determination"""
    pacing = generation_agent._determine_pacing(sample_intervention_spec)
    
    assert pacing in ["slow", "moderate", "gentle"]


def test_get_voice_parameters(generation_agent, sample_intervention_spec):
    """Test voice parameter retrieval"""
    voice_params = generation_agent._get_voice_parameters(sample_intervention_spec)
    
    assert voice_params.voice_id is not None
    assert 0.0 <= voice_params.stability <= 1.0
    assert 0.0 <= voice_params.similarity_boost <= 1.0
    assert voice_params.style == sample_intervention_spec.target_emotion


def test_retrieve_style_parameters(generation_agent, sample_intervention_spec):
    """Test style parameter retrieval"""
    style_params = generation_agent.retrieve_style_parameters(sample_intervention_spec)
    
    assert style_params.tone is not None
    assert style_params.language_style is not None
    assert style_params.imagery_style is not None
    assert style_params.color_palette is not None
    assert style_params.voice_style is not None


def test_extract_emphasis_points(generation_agent):
    """Test emphasis point extraction"""
    script = "Take a moment to breathe. You are safe. You can let go. Trust yourself."
    spec = InterventionSpec(
        therapeutic_framework="CBT",
        target_emotion="calm",
        content_theme="grounding",
        visual_guidelines="",
        text_guidelines="",
        therapeutic_intent=""
    )
    
    emphasis_points = generation_agent._extract_emphasis_points(script, spec)
    
    assert isinstance(emphasis_points, list)
    assert len(emphasis_points) <= 5
    # Should find some of these phrases
    assert any(point in ["breathe", "you are", "you can", "trust yourself"] for point in emphasis_points)


def test_create_placeholder_image(generation_agent):
    """Test placeholder image creation"""
    try:
        image_data = generation_agent._create_placeholder_image("grounding")
        
        assert isinstance(image_data, bytes)
        assert len(image_data) > 0
    except ImportError:
        # PIL not available, should still return minimal PNG
        image_data = generation_agent._create_placeholder_image("grounding")
        assert isinstance(image_data, bytes)


def test_voiceover_script_generation_with_template(generation_agent, sample_intervention_spec):
    """Test voiceover script generation using templates"""
    # Create a mock visual content
    from src.models.intervention import VisualContent
    
    visual = VisualContent(
        image_url="test.png",
        image_data=b"test",
        generation_prompt="peaceful forest scene",
        freepik_metadata={}
    )
    
    script = generation_agent.generate_voiceover_script(sample_intervention_spec, visual)
    
    assert script is not None
    assert script.script_text is not None
    assert len(script.script_text) > 0
    assert 30 <= script.duration_seconds <= 60
    assert script.pacing in ["slow", "moderate", "gentle"]
    assert isinstance(script.emphasis_points, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
