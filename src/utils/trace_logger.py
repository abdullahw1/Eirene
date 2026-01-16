"""Trace logging system for observability"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class TraceLogger:
    """Logger for agent actions and errors with cycle organization"""
    
    def __init__(self, traces_dir: str):
        """
        Initialize trace logger
        
        Args:
            traces_dir: Base directory for trace files
        """
        self.traces_dir = Path(traces_dir)
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        self._action_counters: Dict[str, int] = {}
    
    def create_cycle_directory(self, cycle_id: str) -> Path:
        """
        Create a directory for a specific execution cycle
        
        Args:
            cycle_id: Unique identifier for the cycle
            
        Returns:
            Path to the cycle directory
        """
        cycle_dir = self.traces_dir / cycle_id
        cycle_dir.mkdir(parents=True, exist_ok=True)
        self._action_counters[cycle_id] = 0
        return cycle_dir
    
    def log_agent_action(
        self,
        agent: str,
        action: str,
        data: Dict[str, Any],
        cycle_id: str,
        status: str = "success"
    ) -> None:
        """
        Log an agent action to the traces directory
        
        Args:
            agent: Agent identifier (e.g., "monitor", "strategy")
            action: Action type (e.g., "scan_complete", "mapping_complete")
            data: Action-specific data to log
            cycle_id: Unique identifier for the execution cycle
            status: Action status ("success", "failed", "in_progress")
        """
        cycle_dir = self.traces_dir / cycle_id
        cycle_dir.mkdir(parents=True, exist_ok=True)
        
        # Increment action counter for this cycle
        if cycle_id not in self._action_counters:
            self._action_counters[cycle_id] = 0
        self._action_counters[cycle_id] += 1
        
        # Create trace entry
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "cycle_id": cycle_id,
            "agent": agent,
            "action": action,
            "data": data,
            "status": status
        }
        
        # Write to numbered file
        action_num = str(self._action_counters[cycle_id]).zfill(2)
        filename = f"{action_num}_{agent}_{action}.json"
        trace_file = cycle_dir / filename
        
        with open(trace_file, "w") as f:
            json.dump(trace_entry, f, indent=2, default=str)
    
    def log_error(
        self,
        agent: str,
        error: Exception,
        context: Dict[str, Any],
        cycle_id: str
    ) -> None:
        """
        Log an error to the traces directory
        
        Args:
            agent: Agent identifier where error occurred
            error: Exception that was raised
            context: Additional context about the error
            cycle_id: Unique identifier for the execution cycle
        """
        cycle_dir = self.traces_dir / cycle_id
        cycle_dir.mkdir(parents=True, exist_ok=True)
        
        # Create error entry
        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "cycle_id": cycle_id,
            "agent": agent,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "stack_trace": self._get_stack_trace(error)
        }
        
        # Append to errors file
        errors_file = cycle_dir / "errors.json"
        
        # Read existing errors if file exists
        errors = []
        if errors_file.exists():
            with open(errors_file, "r") as f:
                try:
                    errors = json.load(f)
                    if not isinstance(errors, list):
                        errors = [errors]
                except json.JSONDecodeError:
                    errors = []
        
        # Append new error
        errors.append(error_entry)
        
        # Write back to file
        with open(errors_file, "w") as f:
            json.dump(errors, f, indent=2, default=str)
    
    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """Extract stack trace from exception"""
        import traceback
        return "".join(traceback.format_exception(type(error), error, error.__traceback__))
    
    def get_cycle_traces(self, cycle_id: str) -> list:
        """
        Retrieve all trace entries for a specific cycle
        
        Args:
            cycle_id: Unique identifier for the cycle
            
        Returns:
            List of trace entries
        """
        cycle_dir = self.traces_dir / cycle_id
        if not cycle_dir.exists():
            return []
        
        traces = []
        for trace_file in sorted(cycle_dir.glob("*.json")):
            if trace_file.name != "errors.json":
                with open(trace_file, "r") as f:
                    traces.append(json.load(f))
        
        return traces
    
    def get_cycle_errors(self, cycle_id: str) -> list:
        """
        Retrieve all errors for a specific cycle
        
        Args:
            cycle_id: Unique identifier for the cycle
            
        Returns:
            List of error entries
        """
        errors_file = self.traces_dir / cycle_id / "errors.json"
        if not errors_file.exists():
            return []
        
        with open(errors_file, "r") as f:
            try:
                errors = json.load(f)
                return errors if isinstance(errors, list) else [errors]
            except json.JSONDecodeError:
                return []
