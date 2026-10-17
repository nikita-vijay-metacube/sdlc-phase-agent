import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class PhaseDetector:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "AQ.Ab8RN6LFD56PfPqB6tKFogdhLtY_xvghhuhEdCXBV_3bVo6b1A":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False

        self.valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]

    def detect_phase(self, description: str) -> tuple[str, str]:
        if not self.enabled:
            return self._fallback_detection(description)

        prompt = (
            f"Classify this feature request into one SDLC phase:\n\n"
            f'"{description}"\n\n'
            f"Phases: {', '.join(self.valid_phases)}\n\n"
            f"Respond strictly in this format: phase_name | confidence (High/Medium/Low)"
        )

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

            return phase, confidence

        except Exception as e:
            print(f"\n[API Error] Gemini request failed: {e}. Using fallback detection.")
            return self._fallback_detection(description)

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