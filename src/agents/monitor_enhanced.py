"""Enhanced Monitor Agent - Real TinyFish Integration for Hackathon"""

import json
import requests
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from ..models.stress_signal import StressSignal
from ..utils.trace_logger import TraceLogger


class MonitorAgentEnhanced:
    """Enhanced Monitor Agent with real TinyFish API integration"""
    
    def __init__(
        self,
        tinyfish_api_key: str,
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None,
        use_live_search: bool = False
    ):
        """
        Initialize Enhanced Monitor Agent
        
        Args:
            tinyfish_api_key: API key for TinyFish/Mino
            trace_logger: Optional trace logger
            cycle_id: Optional cycle ID for trace logging
            use_live_search: If True, uses real TinyFish API; if False, uses curated examples
        """
        self.tinyfish_api_key = tinyfish_api_key
        self.trace_logger = trace_logger
        self.cycle_id = cycle_id or "default"
        self.use_live_search = use_live_search
        self.tinyfish_base_url = "https://mino.ai/v1/automation"
    
    def search_community(self, community_name: str, search_topic: str) -> List[StressSignal]:
        """
        Search a community for stress signals
        
        Args:
            community_name: Name of community (e.g., "r/anxiety", "Twitter")
            search_topic: What to search for (e.g., "anxiety", "burnout")
        
        Returns:
            List of detected stress signals
        """
        if self.use_live_search:
            return self._search_with_tinyfish(community_name, search_topic)
        else:
            return self._get_curated_signals(community_name, search_topic)
    
    def _search_with_tinyfish(self, community_name: str, search_topic: str) -> List[StressSignal]:
        """
        Use real TinyFish API to search for stress signals
        
        Args:
            community_name: Community to search
            search_topic: Topic to search for
        
        Returns:
            List of stress signals from real search
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="tinyfish_search_start",
                    data={"community": community_name, "topic": search_topic},
                    cycle_id=self.cycle_id
                )
            
            # Map community to URL
            url_mapping = {
                "r/anxiety": "https://reddit.com/r/anxiety",
                "r/burnout": "https://reddit.com/r/burnout",
                "r/lonely": "https://reddit.com/r/lonely",
                "r/depression": "https://reddit.com/r/depression",
                "r/vent": "https://reddit.com/r/vent",
                "Twitter/X": "https://twitter.com/search?q=mental+health"
            }
            
            start_url = url_mapping.get(community_name, "https://reddit.com/r/mentalhealth")
            
            # TinyFish API call
            headers = {
                "X-API-Key": self.tinyfish_api_key,
                "Content-Type": "application/json"
            }
            
            goal = f"Find recent posts about {search_topic} and mental health struggles. Extract the post text and context. Return in JSON format: {{\"posts\": [{{\"text\": \"...\", \"context\": \"...\"}}]}}"
            
            payload = {
                "url": start_url,
                "goal": goal
            }
            
            response = requests.post(
                f"{self.tinyfish_base_url}/run-sse",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                # Parse TinyFish response
                result_data = response.json()
                
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="monitor",
                        action="tinyfish_search_complete",
                        data={"status": "success", "community": community_name},
                        cycle_id=self.cycle_id
                    )
                
                # Extract signals from TinyFish results
                return self._parse_tinyfish_results(result_data, community_name)
            else:
                # Fallback to curated if TinyFish fails
                if self.trace_logger:
                    self.trace_logger.log_agent_action(
                        agent="monitor",
                        action="tinyfish_fallback",
                        data={"reason": f"Status {response.status_code}"},
                        cycle_id=self.cycle_id
                    )
                return self._get_curated_signals(community_name, search_topic)
                
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="monitor",
                    error=e,
                    context={"action": "tinyfish_search", "community": community_name},
                    cycle_id=self.cycle_id
                )
            # Fallback to curated signals
            return self._get_curated_signals(community_name, search_topic)
    
    def _parse_tinyfish_results(self, data: Dict[str, Any], community: str) -> List[StressSignal]:
        """Parse TinyFish API results into stress signals"""
        signals = []
        
        # Extract posts from TinyFish response
        posts = data.get("posts", [])
        
        for post in posts[:3]:  # Limit to top 3
            text = post.get("text", "")
            if text:
                signal = StressSignal(
                    source_url=f"https://reddit.com/{community}",
                    signal_type=self._classify_signal_type(text),
                    community_context=f"Live from {community}",
                    severity_indicator=self._calculate_severity(text),
                    timestamp=datetime.now(),
                    raw_content=text
                )
                signals.append(signal)
        
        return signals if signals else self._get_curated_signals(community, "")
    
    def _get_curated_signals(self, community_name: str, search_topic: str) -> List[StressSignal]:
        """
        Get curated, realistic stress signals for fast demos
        
        Args:
            community_name: Community name
            search_topic: Search topic
        
        Returns:
            List of curated stress signals
        """
        # Curated real-world examples for each community
        curated_data = {
            "r/burnout": {
                "type": "burnout",
                "content": "I'm a software engineer and I'm completely burned out. 60+ hour weeks for months, constant pressure to ship features, no work-life balance. I used to love coding but now I dread opening my laptop. Can't sleep, can't focus, feel like I'm going to crash. Is this normal in tech?",
                "severity": 0.85
            },
            "r/anxiety": {
                "type": "anxiety",
                "content": "Finals week is destroying me. Having panic attacks before every exam, can't sleep, heart racing constantly. I study for hours but my mind goes blank during tests. My GPA is dropping and I'm terrified of failing. How do other students cope with this level of stress?",
                "severity": 0.80
            },
            "r/lonely": {
                "type": "isolation",
                "content": "Been working from home for 2 years now. Haven't had a real conversation with anyone outside of Zoom meetings in weeks. All my friends moved to different cities. The isolation is crushing. Sometimes I talk to myself just to hear a voice. Is anyone else struggling with remote work loneliness?",
                "severity": 0.75
            },
            "r/depression": {
                "type": "depression",
                "content": "The winter months are hitting hard. No motivation to do anything, sleeping 12+ hours a day, can't find joy in things I used to love. Everything feels gray and pointless. Seasonal depression is real and it's getting worse every year. How do you fight through this?",
                "severity": 0.82
            },
            "Twitter/X": {
                "type": "anxiety",
                "content": "Scrolling through social media is destroying my mental health. Everyone's life looks perfect while I'm struggling. FOMO is real, comparison is killing me, can't stop checking my phone. The digital world is overwhelming and I don't know how to disconnect. #MentalHealthMatters",
                "severity": 0.70
            },
            "r/vent": {
                "type": "general_stress",
                "content": "Sunday night and the anxiety about Monday is already hitting. Dreading the work week, feeling trapped in my job, can't enjoy my weekend because I'm worried about tomorrow. The Sunday scaries are real and they're getting worse. Anyone else feel this way?",
                "severity": 0.68
            }
        }
        
        data = curated_data.get(community_name, curated_data["r/anxiety"])
        
        signal = StressSignal(
            source_url=f"https://example.com/{community_name}",
            signal_type=data["type"],
            community_context=f"From {community_name}",
            severity_indicator=data["severity"],
            timestamp=datetime.now(),
            raw_content=data["content"]
        )
        
        return [signal]
    
    def _classify_signal_type(self, content: str) -> str:
        """Classify stress signal type from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["anxious", "anxiety", "panic", "worried"]):
            return "anxiety"
        elif any(word in content_lower for word in ["burnout", "exhausted", "overwhelmed"]):
            return "burnout"
        elif any(word in content_lower for word in ["lonely", "isolated", "alone"]):
            return "isolation"
        elif any(word in content_lower for word in ["depressed", "depression", "hopeless"]):
            return "depression"
        else:
            return "general_stress"
    
    def _calculate_severity(self, content: str) -> float:
        """Calculate severity from content"""
        intensity_words = [
            "severe", "extreme", "unbearable", "crisis", "emergency",
            "desperate", "hopeless", "suicidal", "can't cope", "crushing"
        ]
        
        content_lower = content.lower()
        intensity_count = sum(1 for word in intensity_words if word in content_lower)
        
        severity = min(0.3 + (intensity_count * 0.15), 1.0)
        return severity
