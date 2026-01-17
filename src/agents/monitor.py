"""Monitor Agent - Detects stress signals from web sources using TinyFish MCP"""

import json
import subprocess
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from ..models.stress_signal import StressSignal
from ..utils.trace_logger import TraceLogger


class MonitorAgent:
    """Agent A: Scans web sources for community stress signals using TinyFish MCP"""
    
    def __init__(
        self,
        agentql_api_key: str,
        trace_logger: Optional[TraceLogger] = None,
        cycle_id: Optional[str] = None
    ):
        """
        Initialize Monitor Agent
        
        Args:
            agentql_api_key: API key for AgentQL
            trace_logger: Optional trace logger for observability
            cycle_id: Optional cycle ID for trace logging
        """
        self.agentql_api_key = agentql_api_key
        self.trace_logger = trace_logger
        self.cycle_id = cycle_id or "default"
        self.mcp_process: Optional[subprocess.Popen] = None
    
    def connect_tinyfish_mcp(self) -> bool:
        """
        Connect to TinyFish MCP server using AgentQL
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="connect_mcp_start",
                    data={"status": "connecting"},
                    cycle_id=self.cycle_id
                )
            
            # TinyFish MCP uses AgentQL via npx
            # Command: env AGENTQL_API_KEY={key} npx -y agentql-mcp
            # For this implementation, we'll verify the key is present
            # Actual MCP connection would be established here
            
            if not self.agentql_api_key:
                raise ValueError("AgentQL API key is required")
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="connect_mcp_complete",
                    data={"status": "connected"},
                    cycle_id=self.cycle_id
                )
            
            return True
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="monitor",
                    error=e,
                    context={"action": "connect_tinyfish_mcp"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def scan_web_sources(self) -> List[StressSignal]:
        """
        Scan web sources for stress signals using AgentQL queries
        
        Returns:
            List of detected stress signals
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="scan_start",
                    data={"status": "scanning"},
                    cycle_id=self.cycle_id
                )
            
            # In a real implementation, this would:
            # 1. Use AgentQL to query web sources (Reddit, forums, social media)
            # 2. Extract stress-related content
            # 3. Parse and structure the data
            
            # For now, we'll simulate finding stress signals
            # This would be replaced with actual AgentQL queries
            signals = self._query_web_sources()
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="scan_complete",
                    data={
                        "signals_found": len(signals),
                        "signal_types": [s.signal_type for s in signals]
                    },
                    cycle_id=self.cycle_id
                )
            
            return signals
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="monitor",
                    error=e,
                    context={"action": "scan_web_sources"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _query_web_sources(self) -> List[StressSignal]:
        """
        Internal method to query web sources using AgentQL
        
        Returns:
            List of raw stress signals
        """
        # This is a placeholder for actual AgentQL integration
        # In production, this would use the TinyFish MCP server
        # to query Reddit, forums, and other web sources
        
        # Example sources to query:
        # - reddit.com/r/anxiety
        # - reddit.com/r/depression
        # - reddit.com/r/mentalhealth
        # - Various mental health forums
        
        signals = []
        
        # Placeholder: In real implementation, this would use AgentQL
        # to extract structured data from web pages
        
        return signals
    
    def extract_signal_metadata(self, raw_data: Dict[str, Any]) -> StressSignal:
        """
        Extract structured stress signal from raw web data
        
        Args:
            raw_data: Raw data from web source containing:
                - url: Source URL
                - content: Text content
                - timestamp: When content was posted
                - Additional metadata
        
        Returns:
            Structured StressSignal object
        """
        try:
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="extract_metadata_start",
                    data={"source": raw_data.get("url", "unknown")},
                    cycle_id=self.cycle_id
                )
            
            # Extract signal type from content analysis
            signal_type = self._classify_signal_type(raw_data.get("content", ""))
            
            # Calculate severity indicator (0.0 to 1.0)
            severity = self._calculate_severity(raw_data.get("content", ""))
            
            # Extract community context
            community_context = self._extract_community_context(raw_data)
            
            # Create structured signal
            signal = StressSignal(
                source_url=raw_data.get("url", ""),
                signal_type=signal_type,
                community_context=community_context,
                severity_indicator=severity,
                timestamp=raw_data.get("timestamp", datetime.now()),
                raw_content=raw_data.get("content", "")
            )
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="extract_metadata_complete",
                    data={
                        "signal_type": signal_type,
                        "severity": severity
                    },
                    cycle_id=self.cycle_id
                )
            
            return signal
            
        except Exception as e:
            if self.trace_logger:
                self.trace_logger.log_error(
                    agent="monitor",
                    error=e,
                    context={"action": "extract_signal_metadata"},
                    cycle_id=self.cycle_id
                )
            raise
    
    def _classify_signal_type(self, content: str) -> str:
        """
        Classify the type of stress signal from content
        
        Args:
            content: Text content to analyze
        
        Returns:
            Signal type (e.g., "anxiety", "burnout", "isolation")
        """
        content_lower = content.lower()
        
        # Simple keyword-based classification
        # In production, this would use NLP/LLM for better classification
        if any(word in content_lower for word in ["anxious", "anxiety", "worried", "panic"]):
            return "anxiety"
        elif any(word in content_lower for word in ["burnout", "exhausted", "overwhelmed"]):
            return "burnout"
        elif any(word in content_lower for word in ["lonely", "isolated", "alone"]):
            return "isolation"
        elif any(word in content_lower for word in ["depressed", "depression", "sad"]):
            return "depression"
        else:
            return "general_stress"
    
    def _calculate_severity(self, content: str) -> float:
        """
        Calculate severity indicator from content
        
        Args:
            content: Text content to analyze
        
        Returns:
            Severity score between 0.0 and 1.0
        """
        # Simple heuristic based on intensity words
        # In production, this would use sentiment analysis
        intensity_words = [
            "severe", "extreme", "unbearable", "crisis", "emergency",
            "desperate", "hopeless", "suicidal", "can't cope"
        ]
        
        content_lower = content.lower()
        intensity_count = sum(1 for word in intensity_words if word in content_lower)
        
        # Normalize to 0.0-1.0 range
        severity = min(0.3 + (intensity_count * 0.15), 1.0)
        
        return severity
    
    def _extract_community_context(self, raw_data: Dict[str, Any]) -> str:
        """
        Extract community context from raw data
        
        Args:
            raw_data: Raw data containing community information
        
        Returns:
            Community context string
        """
        url = raw_data.get("url", "")
        
        # Extract community from URL
        if "reddit.com/r/" in url:
            # Extract subreddit name
            parts = url.split("/r/")
            if len(parts) > 1:
                subreddit = parts[1].split("/")[0]
                return f"Reddit community: r/{subreddit}"
        
        # Default context
        return "General online community"
    
    def disconnect(self):
        """Disconnect from TinyFish MCP server"""
        if self.mcp_process:
            self.mcp_process.terminate()
            self.mcp_process = None
            
            if self.trace_logger:
                self.trace_logger.log_agent_action(
                    agent="monitor",
                    action="disconnect_mcp",
                    data={"status": "disconnected"},
                    cycle_id=self.cycle_id
                )
