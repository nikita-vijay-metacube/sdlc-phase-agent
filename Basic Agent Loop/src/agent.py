from collections import deque
from src.phase_detector import PhaseDetector

class SimpleAgent:
    def __init__(self, memory_limit: int = 2):
        self.phase_detector = PhaseDetector()
        self.memory = deque(maxlen=memory_limit)

    def observe(self, user_input: str) -> dict:
        """Collect basic information about the request and context."""
        cleaned_input = user_input.strip()
        observation = {
            "input": cleaned_input,
            "length": len(cleaned_input),
            "recent_history": list(self.memory)
        }
        return observation

    def reason(self, observations: dict) -> dict:
        """Use the phase detector and context to analyze the request."""
        description = observations["input"]
        
        # Detect phase and confidence using Gemini/fallback
        phase, confidence = self.phase_detector.detect_phase(description)
        
        # Build reasoning narrative
        reasoning_text = f"Analyzed description ({observations['length']} chars). "
        if observations["recent_history"]:
            reasoning_text += f"Factored in context from previous {len(observations['recent_history'])} request(s). "
        reasoning_text += f"Mapped to SDLC phase '{phase}' with '{confidence}' confidence."

        return {
            "phase": phase,
            "confidence": confidence,
            "reasoning": reasoning_text
        }

    def act(self, reasoning: dict, user_input: str) -> dict:
        """Generate response, advice, and update memory."""
        phase = reasoning["phase"]
        
        # Provide targeted advice based on the detected phase
        advice_map = {
            "requirements": "Advice: Document clear user stories and acceptance criteria.",
            "design": "Advice: Draft wireframes or architecture diagrams before implementation.",
            "implementation": "Advice: Keep code modular and follow project style guidelines.",
            "testing": "Advice: Ensure edge cases and unit test coverage are verified.",
            "deployment": "Advice: Verify staging environments and configure monitoring."
        }
        advice = advice_map.get(phase, "Advice: Proceed systematically through the SDLC.")

        # Save current interaction to memory (last 2 interactions)
        self.memory.append({"input": user_input, "phase": phase})

        return {
            "phase": phase,
            "confidence": reasoning["confidence"],
            "reasoning": reasoning["reasoning"],
            "advice": advice
        }

    def process_request(self, user_input: str) -> dict:
        """Executes the full Observe -> Reason -> Act cycle."""
        obs = self.observe(user_input)
        reasoning = self.reason(obs)
        action = self.act(reasoning, user_input)
        return action