from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class FeatureRequest:
    description: str
    client: str
    project: str
    phase: str = "Unassigned"
    confidence: str = "N/A"
    advice: str = "N/A"
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @staticmethod
    def validate_description(description: str) -> tuple[bool, str]:
        """Validates that the description is between 10 and 500 characters."""
        cleaned = description.strip()
        if len(cleaned) < 10:
            return False, "Description is too short. It must be at least 10 characters."
        if len(cleaned) > 500:
            return False, "Description is too long. It must be under 500 characters."
        return True, ""