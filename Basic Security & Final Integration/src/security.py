import re
import time
from typing import Tuple

class SecurityManager:
    def __init__(self, rate_limit_seconds: float = 1.0):
        self.rate_limit_seconds = rate_limit_seconds
        self.last_call_timestamp = 0.0

    def sanitize_input(self, text: str) -> str:
        """Basic sanitization: strips HTML tags and normalizes whitespace."""
        if not text:
            return ""
        # Remove HTML/XML tags
        clean_text = re.sub(r'<[^>]*>', '', text)
        # Normalize whitespace
        clean_text = " ".join(clean_text.split())
        return clean_text

    def validate_request_description(self, description: str) -> Tuple[bool, str]:
        """Validates length constraints and content safety."""
        sanitized = self.sanitize_input(description)
        
        if len(sanitized) < 10:
            return False, "Description is too short. Minimum requirement is 10 characters."
        if len(sanitized) > 500:
            return False, "Description is too long. Maximum limit is 500 characters."
            
        # Check for suspicious injection patterns
        if re.search(r'(javascript:|<script|\bexec\b|\beval\b)', sanitized, re.IGNORECASE):
            return False, "Input contains prohibited or potentially unsafe patterns."

        return True, sanitized

    def check_rate_limit(self) -> Tuple[bool, str]:
        """Simple client-side rate limiter to prevent API request spamming."""
        current_time = time.time()
        elapsed = current_time - self.last_call_timestamp
        
        if elapsed < self.rate_limit_seconds:
            wait_time = round(self.rate_limit_seconds - elapsed, 1)
            return False, f"Rate limit active. Please wait {wait_time}s before submitting another request."
            
        self.last_call_timestamp = current_time
        return True, ""