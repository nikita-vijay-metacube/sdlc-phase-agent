import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)

class LangChainStyleAgent:
    def __init__(self, memory_window: int = 2):
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key and api_key != "your_actual_gemini_api_key":
            print(f"[Debug] Gemini API Key loaded successfully!")
            genai.configure(api_key=api_key)
            try:
                self.model = genai.GenerativeModel('gemini-3.8-flash')
                self.enabled = True
                print("[Debug] Successfully initialized model: gemini-3.8-flash")
            except Exception as e:
                print(f"[Debug] Error initializing model: {e}. Using fallback heuristics.")
                self.enabled = False
        else:
            print("[Debug] Warning: GEMINI_API_KEY not found or is a placeholder. Using heuristic fallback.")
            self.enabled = False

        self.valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]
        self.memory = []
        self.memory_window = memory_window

    def _format_prompt(self, description: str) -> str:
        """Enhanced PromptTemplate with clear phase guidelines and few-shot examples."""
        history_str = "\n".join([f"- {m['input']} (Phase: {m['phase']})" for m in self.memory]) or "None"
        
        template = f"""You are an expert Software Engineering Project Manager specializing in Software Development Life Cycle (SDLC) classification.

Classify the given feature request into exactly one of the following SDLC phases based on its primary intent:
- requirements: Gathering user needs, defining user stories, business rules, or feature scope.
- design: System architecture, UI/UX mockups, wireframing, or database schema planning.
- implementation: Writing source code, building features, or coding endpoints.
- testing: Running unit/integration tests, quality assurance, verification, or bug checks.
- deployment: Release management, server hosting setup, CI/CD pipeline, or publishing updates.

Examples:
- "Gather stakeholder requirements for user signup" -> requirements | High
- "Draft wireframes and database architecture schemas" -> design | High
- "Write backend API code for payment processing" -> implementation | High
- "Run automated test suites and verify bug fixes" -> testing | High
- "Configure production server and deploy release" -> deployment | High

Context (Recent Requests):
{history_str}

Request: "{description}"

Respond strictly in this format:
phase_name | confidence (High/Medium/Low)
"""
        return template

    def process_request(self, description: str) -> dict:
        phase, confidence, reasoning = "implementation", "Medium", "Analyzed via enhanced prompt template."

        if self.enabled:
            prompt = self._format_prompt(description)
            try:
                response = self.model.generate_content(prompt)
                content = response.text.strip()
                
                if "|" in content:
                    parts = content.split("|")
                    phase = parts[0].strip().lower()
                    confidence = parts[1].strip()
                else:
                    phase = content.lower()
                    confidence = "Medium"

                if phase not in self.valid_phases:
                    phase = "implementation"
                    confidence = "Low"
                
                reasoning = f"Enhanced Gemini Agent processed request. Mapped to '{phase}' with '{confidence}' confidence."

            except Exception as e:
                reasoning = f"API error encountered ({e}), used fallback heuristics."
                phase, confidence = self._fallback_detection(description)
        else:
            phase, confidence = self._fallback_detection(description)
            reasoning = "Gemini key not configured; used clean prompt heuristic fallback."

        # Generate targeted advice
        advice_map = {
            "requirements": "Advice: Document clear user stories and acceptance criteria.",
            "design": "Advice: Draft wireframes or architecture diagrams before implementation.",
            "implementation": "Advice: Keep code modular and follow project style guidelines.",
            "testing": "Advice: Ensure edge cases and unit test coverage are verified.",
            "deployment": "Advice: Verify staging environments and configure monitoring."
        }
        advice = advice_map.get(phase, "Advice: Proceed systematically through the SDLC.")

        # Update memory buffer
        self.memory.append({"input": description, "phase": phase})
        if len(self.memory) > self.memory_window:
            self.memory.pop(0)

        return {
            "phase": phase,
            "confidence": confidence,
            "reasoning": reasoning,
            "advice": advice
        }

    def _fallback_detection(self, description: str) -> tuple[str, str]:
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["test", "bug", "verify"]):
            return "testing", "Medium (Fallback)"
        elif any(w in desc_lower for w in ["deploy", "release", "host"]):
            return "deployment", "Medium (Fallback)"
        elif any(w in desc_lower for w in ["design", "ui", "ux", "wireframe"]):
            return "design", "Medium (Fallback)"
        elif any(w in desc_lower for w in ["login", "database", "system", "pay"]):
            return "implementation", "Medium (Fallback)"
        return "requirements", "Low (Fallback)"