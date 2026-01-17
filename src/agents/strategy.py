"""Strategy Agent - Maps stress signals to therapeutic frameworks using Yutori"""

import json
import requests
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from ..models.stress_signal import StressSignal
from ..models.intervention import InterventionSpec
from ..utils.trace_logger import TraceLogger


class TherapeuticContext:
    """Context from therapeutic knowledge base"""
    
    def __init__(
        self,
        framework: str,
        techniques: List[str],
        clinical_rationale: str,
        yutori_references: List[str]
    ):
        self.framework = framework
        self.techniques = techniques
        self.clinical_rationale = clinical_rationale
        self.yutori_references = yutori_references


class StrategyAgent:
    """Agent B: Maps stress signals to CBT/DBT frameworks using Yutori knowledge base"""
    
    def __init__(
        self,
        yutori_api_key: str,
        yutori_base_url: str,
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None
    ):
        """
        Initialize Strategy Agent
        
        Args:
            yutori_api_key: API key for Yutori
            yutori_base_url: Base URL for Yutori API
            trace_logger: Optional trace logger for observability
            cycle_id: Optional cycle ID for trace logging
        """
        self.yutori_api_key = yutori_api_key
        self.yutori_base_url = yutori_base_url
        self.trace_logger = trace_logger
        self.cycle_id = cycle_id or "default"
    
    def query_therapeutic_frameworks(self, signal: StressSignal) -> TherapeuticContext:
        """
        Query Yutori knowledge base for relevant therapeutic frameworks
        
        Args:
            signal: Stress signal to analyze
        
        Returns:
            Therapeutic context with framework and techniques
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="query_frameworks_start",
                    data={
                        "signal_type": signal.signal_type,
                        "severity": signal.severity_indicator
                    },
                    cycle_id=self.cycle_id
                )
            
            # Build semantic search query for Yutori
            query = self._build_therapeutic_query(signal)
            
            # Query Yutori knowledge base
            # In production, this would make an actual API call to Yutori
            # For now, we'll use rule-based mapping
            context = self._retrieve_from_yutori(query, signal)
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="query_frameworks_complete",
                    data={
                        "framework": context.framework,
                        "techniques": context.techniques
                    },
                    cycle_id=self.cycle_id
                )
            
            return context
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="strategy",
                    error=e,
                    context={"action": "query_therapeutic_frameworks"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _build_therapeutic_query(self, signal: StressSignal) -> str:
        """
        Build semantic search query for Yutori
        
        Args:
            signal: Stress signal to query about
        
        Returns:
            Query string for Yutori semantic search
        """
        # Combine signal information into a query
        query = f"{signal.signal_type} {signal.community_context} CBT DBT mental health therapy"
        return query
    
    def _retrieve_from_yutori(self, query: str, signal: StressSignal) -> TherapeuticContext:
        """
        Retrieve therapeutic context from Yutori knowledge base using Research API
        
        Args:
            query: Search query
            signal: Original stress signal
        
        Returns:
            Therapeutic context
        """
        # Try to query Yutori Research API for real therapeutic knowledge
        try:
            # Yutori Research API endpoint
            url = f"{self.yutori_base_url}/v1/research/tasks"
            
            headers = {
                "X-API-Key": self.yutori_api_key,
                "Content-Type": "application/json"
            }
            
            # Create a focused research query
            research_query = f"What are the most effective {query} therapeutic techniques and interventions? Focus on evidence-based CBT and DBT approaches."
            
            payload = {
                "query": research_query
            }
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="yutori_research_start",
                    data={"query": research_query},
                    cycle_id=self.cycle_id
                )
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code in [200, 202]:  # 202 = Accepted (queued)
                result_data = response.json()
                task_id = result_data.get('task_id')
                
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="strategy",
                        action="yutori_research_queued",
                        data={
                            "task_id": task_id,
                            "status": result_data.get('status'),
                            "view_url": result_data.get('view_url')
                        },
                        cycle_id=self.cycle_id
                    )
                
                # Note: For real-time use, we'd need to poll for results
                # For now, we'll use the fallback but log that Yutori is available
                
        except Exception as e:
            # Log the error but continue with fallback
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="yutori_research_fallback",
                    data={"error": str(e), "using": "rule_based_mapping"},
                    cycle_id=self.cycle_id
                )
        
        # Use rule-based mapping (clinical fallback)
        # This ensures instant responses while Yutori research runs in background
        framework_mapping = {
            "anxiety": (
                "CBT", 
                ["cognitive_reframing", "breathing_exercises", "grounding"],
                "CBT is highly effective for anxiety through cognitive restructuring of anxious thoughts, "
                "combined with breathing exercises to manage physiological symptoms and grounding techniques "
                "to anchor in the present moment."
            ),
            "burnout": (
                "DBT", 
                ["mindfulness", "self_compassion", "boundary_setting"],
                "DBT provides essential skills for burnout recovery through mindfulness to recognize limits, "
                "self-compassion to counter self-criticism, and boundary-setting to prevent future overwhelm."
            ),
            "isolation": (
                "CBT", 
                ["behavioral_activation", "cognitive_reframing", "self_compassion"],
                "CBT addresses isolation through behavioral activation to increase social engagement, "
                "cognitive reframing of negative self-beliefs, and self-compassion to reduce shame."
            ),
            "depression": (
                "CBT", 
                ["cognitive_reframing", "behavioral_activation", "mindfulness"],
                "CBT is evidence-based for depression, targeting negative thought patterns through cognitive "
                "reframing, increasing activity through behavioral activation, and building awareness through mindfulness."
            ),
            "stress": (
                "CBT", 
                ["breathing_exercises", "mindfulness", "cognitive_reframing"],
                "CBT manages stress through breathing exercises for immediate relief, mindfulness for stress awareness, "
                "and cognitive reframing to reduce stress-inducing thought patterns."
            ),
            "overwhelm": (
                "DBT", 
                ["grounding", "mindfulness", "self_compassion"],
                "DBT helps with overwhelm through grounding techniques to stabilize, mindfulness to create space, "
                "and self-compassion to reduce pressure."
            ),
            "panic": (
                "CBT", 
                ["breathing_exercises", "grounding", "cognitive_reframing"],
                "CBT addresses panic through controlled breathing to regulate physiology, grounding to interrupt "
                "panic cycles, and cognitive reframing to challenge catastrophic thoughts."
            ),
            "grief": (
                "DBT", 
                ["self_compassion", "mindfulness", "emotional_acceptance"],
                "DBT supports grief processing through self-compassion for painful emotions, mindfulness to be "
                "present with grief, and emotional acceptance without judgment."
            )
        }
        
        # Get mapping or use default
        if signal.signal_type in framework_mapping:
            framework, techniques, clinical_rationale = framework_mapping[signal.signal_type]
        else:
            # Default fallback for unknown signal types
            framework = "CBT"
            techniques = ["mindfulness", "self_compassion", "breathing_exercises"]
            clinical_rationale = (
                f"CBT provides evidence-based support for {signal.signal_type} through mindfulness, "
                "self-compassion, and breathing exercises to manage symptoms and build coping skills."
            )
        
        return TherapeuticContext(
            framework=framework,
            techniques=techniques,
            clinical_rationale=clinical_rationale,
            yutori_references=[f"yutori://{framework.lower()}/{signal.signal_type}"]
        )
    
    def map_to_cbt_dbt(self, context: TherapeuticContext) -> InterventionSpec:
        """
        Map therapeutic context to specific CBT/DBT intervention specification
        
        Args:
            context: Therapeutic context from knowledge base
        
        Returns:
            Intervention specification with content guidelines
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="map_to_framework_start",
                    data={"framework": context.framework},
                    cycle_id=self.cycle_id
                )
            
            # Generate intervention spec based on framework and techniques
            spec = self._create_intervention_spec(context)
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="strategy",
                    action="map_to_framework_complete",
                    data={
                        "framework": spec.therapeutic_framework,
                        "theme": spec.content_theme
                    },
                    cycle_id=self.cycle_id
                )
            
            return spec
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="strategy",
                    error=e,
                    context={"action": "map_to_cbt_dbt"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _create_intervention_spec(self, context: TherapeuticContext) -> InterventionSpec:
        """
        Create intervention specification from therapeutic context
        
        Args:
            context: Therapeutic context
        
        Returns:
            Complete intervention specification
        """
        # Determine target emotion based on techniques
        target_emotion = self._determine_target_emotion(context.techniques)
        
        # Determine content theme
        content_theme = self._determine_content_theme(context.techniques)
        
        # Generate visual guidelines
        visual_guidelines = self._generate_visual_guidelines(content_theme, context.framework)
        
        # Generate text guidelines (includes audio/voiceover guidance)
        text_guidelines = self._generate_text_guidelines(context.techniques, context.framework)
        
        # Add audio-specific guidelines
        audio_guidelines = self._generate_audio_guidelines(target_emotion, context.techniques)
        text_guidelines += f" AUDIO PARAMETERS: {audio_guidelines}"
        
        # Generate therapeutic intent
        therapeutic_intent = self._generate_therapeutic_intent(context)
        
        return InterventionSpec(
            therapeutic_framework=context.framework,
            target_emotion=target_emotion,
            content_theme=content_theme,
            visual_guidelines=visual_guidelines,
            text_guidelines=text_guidelines,
            therapeutic_intent=therapeutic_intent
        )
    
    def _generate_audio_guidelines(self, target_emotion: str, techniques: List[str]) -> str:
        """
        Generate audio/voice parameter guidelines for ElevenLabs
        
        Args:
            target_emotion: Target emotional state
            techniques: Therapeutic techniques being used
        
        Returns:
            Audio guidelines string with voice parameters
        """
        # Base voice parameters by target emotion
        voice_params = {
            "calm": "Voice: Soothing, gentle. Stability: 0.65, Similarity: 0.75. Pace: Slow (100-120 wpm). Pitch: Medium-low.",
            "self_acceptance": "Voice: Warm, compassionate. Stability: 0.60, Similarity: 0.80. Pace: Moderate (110-130 wpm). Pitch: Medium.",
            "motivation": "Voice: Encouraging, confident. Stability: 0.70, Similarity: 0.75. Pace: Moderate (120-140 wpm). Pitch: Medium.",
            "present_awareness": "Voice: Clear, centered. Stability: 0.65, Similarity: 0.75. Pace: Slow-moderate (110-125 wpm). Pitch: Medium.",
            "peace": "Voice: Serene, tranquil. Stability: 0.70, Similarity: 0.80. Pace: Very slow (90-110 wpm). Pitch: Low-medium."
        }
        
        base_params = voice_params.get(target_emotion, "Voice: Calm, supportive. Stability: 0.65, Similarity: 0.75. Pace: Moderate (110-130 wpm).")
        
        # Add technique-specific audio adjustments
        adjustments = []
        if "breathing_exercises" in techniques:
            adjustments.append("Include deliberate pauses for breathing (2-3 second gaps)")
        if "grounding" in techniques:
            adjustments.append("Use steady, anchoring rhythm")
        if "mindfulness" in techniques:
            adjustments.append("Maintain even, meditative pacing")
        
        if adjustments:
            base_params += " Special: " + ", ".join(adjustments) + "."
        
        return base_params
    
    def _determine_target_emotion(self, techniques: List[str]) -> str:
        """
        Determine target emotion from techniques
        
        Args:
            techniques: List of therapeutic techniques
        
        Returns:
            Target emotion string
        """
        # Map techniques to target emotions
        if "grounding" in techniques or "breathing_exercises" in techniques:
            return "calm"
        elif "self_compassion" in techniques:
            return "self_acceptance"
        elif "behavioral_activation" in techniques:
            return "motivation"
        elif "mindfulness" in techniques:
            return "present_awareness"
        else:
            return "peace"
    
    def _determine_content_theme(self, techniques: List[str]) -> str:
        """
        Determine content theme from techniques
        
        Args:
            techniques: List of therapeutic techniques
        
        Returns:
            Content theme string
        """
        # Map techniques to content themes
        if "grounding" in techniques:
            return "grounding"
        elif "self_compassion" in techniques:
            return "self_compassion"
        elif "mindfulness" in techniques:
            return "mindfulness"
        elif "behavioral_activation" in techniques:
            return "empowerment"
        else:
            return "relaxation"
    
    def _generate_visual_guidelines(self, theme: str, framework: str) -> str:
        """
        Generate detailed visual content guidelines for Freepik API
        
        Args:
            theme: Content theme
            framework: Therapeutic framework
        
        Returns:
            Detailed visual guidelines string with specific prompts
        """
        visual_templates = {
            "grounding": (
                "Natural grounding scenes: forest floor with moss and stones, beach with sand and shells, "
                "mountain landscape with solid rock formations. Use earth tones (browns, greens, grays). "
                "Include tactile elements that suggest stability and connection to earth. "
                "Lighting: soft, natural daylight. Style: realistic, calming, therapeutic illustration. "
                "Resolution: 1920x1080 minimum. Avoid: busy patterns, harsh contrasts, urban settings."
            ),
            "self_compassion": (
                "Warm, nurturing imagery: gentle sunrise/sunset with soft golden light, cozy safe spaces, "
                "embracing nature scenes (trees sheltering, protective landscapes). Use warm color palette "
                "(soft pinks, warm oranges, gentle yellows, cream). Include elements suggesting care and comfort. "
                "Lighting: warm, diffused, golden hour quality. Style: soft focus, gentle, compassionate. "
                "Resolution: 1920x1080 minimum. Avoid: cold colors, harsh edges, isolating imagery."
            ),
            "mindfulness": (
                "Present-moment awareness scenes: flowing water (streams, gentle waves), swaying grass, "
                "floating clouds, zen garden with raked sand. Use cool, peaceful colors (soft blues, greens, whites). "
                "Include elements suggesting gentle movement and flow. Lighting: soft, even, meditative quality. "
                "Style: minimalist, peaceful, contemplative. Resolution: 1920x1080 minimum. "
                "Avoid: static rigid scenes, busy details, distracting elements."
            ),
            "empowerment": (
                "Uplifting growth imagery: sunrise over mountains, sprouting plants, opening flowers, "
                "paths leading forward, birds in flight. Use inspiring colors (warm golds, vibrant greens, sky blues). "
                "Include elements suggesting progress and possibility. Lighting: bright, hopeful, energizing. "
                "Style: uplifting, dynamic yet calm, inspiring. Resolution: 1920x1080 minimum. "
                "Avoid: obstacles, barriers, downward movement, dark shadows."
            ),
            "relaxation": (
                "Deeply calming scenes: still lakes with reflections, peaceful meadows, soft clouds, "
                "gentle twilight skies, serene beaches. Use soothing color palette (soft blues, lavenders, "
                "pale greens, gentle grays). Include elements suggesting peace and tranquility. "
                "Lighting: soft, diffused, twilight or dawn quality. Style: serene, smooth, peaceful. "
                "Resolution: 1920x1080 minimum. Avoid: sharp contrasts, busy scenes, intense colors."
            )
        }
        
        default_guideline = (
            "Calming therapeutic imagery with soft, peaceful colors. Natural scenes preferred. "
            "Soft lighting, gentle composition. Style: therapeutic illustration, calming, professional. "
            "Resolution: 1920x1080 minimum. Avoid: harsh contrasts, busy patterns, stressful imagery."
        )
        
        return visual_templates.get(theme, default_guideline)
    
    def _generate_text_guidelines(self, techniques: List[str], framework: str) -> str:
        """
        Generate detailed text content guidelines for voiceover script
        
        Args:
            techniques: Therapeutic techniques
            framework: Therapeutic framework
        
        Returns:
            Detailed text guidelines string with specific instructions
        """
        guidelines = f"Use {framework}-based therapeutic language. "
        
        # Add technique-specific guidance
        if "cognitive_reframing" in techniques:
            guidelines += (
                "Include gentle perspective-shifting statements (e.g., 'Notice how you might see this differently'). "
                "Use phrases like 'What if...', 'Consider that...', 'Perhaps...'. "
            )
        if "breathing_exercises" in techniques:
            guidelines += (
                "Guide breathing: 'Breathe in slowly for 4 counts... hold... breathe out for 6 counts'. "
                "Use calming pacing and rhythm. Include pauses for breath. "
            )
        if "mindfulness" in techniques:
            guidelines += (
                "Focus on present-moment awareness: 'Notice what you're feeling right now', "
                "'Bring your attention to this moment'. Use grounding language. "
            )
        if "self_compassion" in techniques:
            guidelines += (
                "Use warm, accepting, nurturing language: 'You deserve kindness', 'Be gentle with yourself'. "
                "Validate feelings without judgment. Speak as a compassionate friend. "
            )
        if "grounding" in techniques:
            guidelines += (
                "Include sensory awareness prompts: 'Notice 5 things you can see, 4 you can touch, 3 you can hear'. "
                "Use concrete, physical anchoring language. "
            )
        if "behavioral_activation" in techniques:
            guidelines += (
                "Include gentle encouragement for action: 'One small step', 'You have the strength'. "
                "Focus on possibility and capability. "
            )
        
        # Add general voiceover guidelines
        guidelines += (
            "Structure: Opening (5-10s) - acknowledge feeling, "
            "Middle (20-40s) - therapeutic technique/exercise, "
            "Closing (5-10s) - affirmation/encouragement. "
            "Keep language simple, direct, and supportive. "
            "Use second person ('you') to create connection. "
            "Pace for calm delivery: approximately 120-140 words per minute. "
            "Target 30-60 seconds total spoken duration. "
            "Tone: warm, calm, reassuring, professional yet personal."
        )
        
        return guidelines
    
    def _generate_therapeutic_intent(self, context: TherapeuticContext) -> str:
        """
        Generate therapeutic intent statement
        
        Args:
            context: Therapeutic context
        
        Returns:
            Therapeutic intent string
        """
        return (
            f"Apply {context.framework} framework using {', '.join(context.techniques[:2])} "
            f"to provide evidence-based support. {context.clinical_rationale}"
        )
    
    def generate_content_guidelines(self, spec: InterventionSpec) -> Dict[str, str]:
        """
        Generate detailed content guidelines from intervention spec
        
        Args:
            spec: Intervention specification
        
        Returns:
            Dictionary of content guidelines
        """
        return {
            "visual": spec.visual_guidelines,
            "text": spec.text_guidelines,
            "therapeutic_intent": spec.therapeutic_intent,
            "framework": spec.therapeutic_framework,
            "theme": spec.content_theme
        }
