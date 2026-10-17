import json
import os
from typing import List, Dict, Any

class JSONStorage:
    def __init__(self, filepath: str = "data/requests.json"):
        self.filepath = filepath
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Ensures the data directory and JSON file exist."""
        dir_name = os.path.dirname(self.filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.exists(self.filepath):
            self.save_all([])

    def load_requests(self) -> List[Dict[str, Any]]:
        """Loads all requests from the JSON file."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def save_all(self, requests: List[Dict[str, Any]]) -> None:
        """Saves the complete list of requests to the JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(requests, f, indent=4)

    def append_request(self, request_dict: Dict[str, Any]) -> None:
        """Appends a single request to storage."""
        requests = self.load_requests()
        requests.append(request_dict)
        self.save_all(requests)