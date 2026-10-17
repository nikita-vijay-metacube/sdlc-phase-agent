import os
import json
from datetime import datetime
from pathlib import Path

class MetricsLogger:
    def __init__(self, log_path: str = "data/agent_audit.log", metrics_path: str = "data/metrics.json"):
        self.log_path = Path(log_path)
        self.metrics_path = Path(metrics_path)
        self._ensure_storage()

    def _ensure_storage(self):
        """Ensures log and metrics storage files exist."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        # NEW: Automatically create empty log file if it doesn't exist
        if not self.log_path.exists():
            self.log_path.touch()

        if not self.metrics_path.exists():
            initial_metrics = {
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "phases_detected": {},
                "total_response_time": 0.0,
                "recent_errors": []
            }
            self._save_metrics(initial_metrics)

    def _load_metrics(self) -> dict:
        try:
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "phases_detected": {},
                "total_response_time": 0.0,
                "recent_errors": []
            }

    def _save_metrics(self, metrics: dict):
        with open(self.metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)

    def log_event(self, description: str, phase: str, success: bool, response_time: float, error: str = None):
        """Logs interaction details to text file and updates aggregated metrics."""
        timestamp = datetime.now().isoformat()
        
        # 1. Text Audit Log Entry
        log_entry = f"[{timestamp}] SUCCESS={str(success).upper()} | PHASE={phase.upper()} | TIME={response_time:.3f}s | DESC={description}"
        if error:
            log_entry += f" | ERROR={error}"
        
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry + "\n")

        # 2. Update Persistent Metrics
        metrics = self._load_metrics()
        metrics["total_interactions"] += 1
        
        if success:
            metrics["successful_interactions"] += 1
        else:
            metrics["failed_interactions"] += 1
            if error:
                metrics["recent_errors"].append(f"[{timestamp}] {error}")
                # Keep only the last 5 errors
                metrics["recent_errors"] = metrics["recent_errors"][-5:]

        metrics["total_response_time"] += response_time

        # Track phase frequency
        if phase:
            phase_lower = phase.lower()
            metrics["phases_detected"][phase_lower] = metrics["phases_detected"].get(phase_lower, 0) + 1

        self._save_metrics(metrics)

    def get_dashboard_stats(self) -> dict:
        """Calculates performance summaries and metrics for display."""
        metrics = self._load_metrics()
        total = metrics["total_interactions"]
        success_rate = (metrics["successful_interactions"] / total * 100) if total > 0 else 0.0
        avg_time = (metrics["total_response_time"] / total) if total > 0 else 0.0

        return {
            "total_interactions": total,
            "success_rate": round(success_rate, 2),
            "phases_detected": metrics["phases_detected"],
            "avg_response_time": round(avg_time, 3),
            "recent_errors": metrics["recent_errors"]
        }