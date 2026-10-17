import os
import json
import time
from datetime import datetime
from pathlib import Path

# Try importing Google Generative AI (falls back gracefully if unavailable)
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv(override=True)
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class SDLCAutonomousAgent:
    def __init__(self, data_dir="data", artifacts_dir="artifacts"):
        self.data_dir = Path(data_dir)
        self.artifacts_dir = Path(artifacts_dir)
        self.requests_file = self.data_dir / "requests.json"
        self.log_file = self.data_dir / "audit.log"
        
        self.valid_phases = ["requirements", "design", "implementation", "testing", "deployment"]
        self.memory = []  # Short-term memory for contextual adaptation
        
        self._setup_storage()
        self._init_llm()

    def _setup_storage(self):
        """Automatically sets up required data directories and artifact subfolders."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for phase in self.valid_phases:
            (self.artifacts_dir / phase).mkdir(parents=True, exist_ok=True)
            
        if not self.requests_file.exists():
            with open(self.requests_file, "w", encoding="utf-8") as f:
                json.dump([], f)
                
        if not self.log_file.exists():
            self.log_file.touch()

    def _init_llm(self):
        """Initializes the Gemini API client if environment key is provided."""
        api_key = os.getenv("GEMINI_API_KEY")
        if GEMINI_AVAILABLE and api_key and api_key != "your_actual_gemini_api_key":
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.llm_active = True
            except Exception:
                self.llm_active = False
        else:
            self.llm_active = False

    # 1. OBSERVE
    def observe(self, user_input: str) -> dict:
        """Collects raw data and recent memory context."""
        cleaned = user_input.strip()
        return {
            "input": cleaned,
            "length": len(cleaned),
            "recent_memory": list(self.memory)
        }

    # 2. REASON (LLM Phase Detection with Heuristic Fallback)
    def reason(self, observation: dict) -> tuple[str, str, str]:
        """Uses LLM reasoning or heuristic fallback to identify SDLC phases."""
        desc = observation["input"]
        
        if self.llm_active:
            try:
                prompt = (
                    f"Classify this feature request into one SDLC phase "
                    f"(requirements, design, implementation, testing, deployment):\n\n"
                    f'"{desc}"\n\n'
                    f"Respond strictly in this format: phase_name | confidence (High/Medium/Low)"
                )
                response = self.model.generate_content(prompt)
                parts = response.text.strip().split("|")
                phase = parts[0].strip().lower()
                confidence = parts[1].strip() if len(parts) > 1 else "Medium"
                
                if phase not in self.valid_phases:
                    phase = "implementation"
                return phase, confidence, "LLM reasoning successfully processed."
            except Exception:
                pass # Falls back to keywords if API hits an error

        # Fallback Heuristics
        desc_lower = desc.lower()
        if any(w in desc_lower for w in ["test", "bug", "qa", "verify"]):
            return "testing", "Medium (Heuristic)", "Keyword match for testing."
        elif any(w in desc_lower for w in ["deploy", "server", "release", "host"]):
            return "deployment", "Medium (Heuristic)", "Keyword match for deployment."
        elif any(w in desc_lower for w in ["design", "ui", "ux", "wireframe", "schema"]):
            return "design", "Medium (Heuristic)", "Keyword match for design."
        elif any(w in desc_lower for w in ["code", "implement", "database", "login"]):
            return "implementation", "Medium (Heuristic)", "Keyword match for implementation."
        return "requirements", "Low (Heuristic)", "Defaulted to requirements phase."

    # 3. ACT (Artifact Generation & Storage)
    def act(self, phase: str, description: str) -> str:
        """Generates phase template document and stores it in organized phase folders."""
        req_id = str(int(time.time()))[-6:]
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        templates = {
            "requirements": f"# Requirements Document\n\n- **ID**: {req_id}\n- **Date**: {date_str}\n- **Description**: {description}\n- **Action**: Review user stories and acceptance criteria with stakeholders.",
            "design": f"# System Design Outline\n\n- **ID**: {req_id}\n- **Date**: {date_str}\n- **Overview**: {description}\n- **Action**: Draft component architecture diagrams and wireframes.",
            "implementation": f"# Implementation Task List\n\n- **ID**: {req_id}\n- **Date**: {date_str}\n- **Feature**: {description}\n- **Action**: Write modular source code and corresponding unit tests.",
            "testing": f"# Test Plan Specifications\n\n- **ID**: {req_id}\n- **Date**: {date_str}\n- **Target**: {description}\n- **Action**: Execute test suite, log bugs, and verify coverage.",
            "deployment": f"# Deployment Checklist\n\n- **ID**: {req_id}\n- **Date**: {date_str}\n- **Release**: {description}\n- **Action**: Run staging checks, deploy code, and monitor release health."
        }
        
        content = templates.get(phase, templates["requirements"])
        filename = f"doc_{req_id}_{phase}.md"
        filepath = self.artifacts_dir / phase / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return str(filepath)

    # 4. ADAPT (Memory Update & Logging)
    def adapt(self, user_input: str, phase: str, success: bool, duration: float):
        """Updates short-term context memory and writes traceability logs."""
        self.memory.append({"input": user_input, "phase": phase})
        if len(self.memory) > 2:
            self.memory.pop(0)  # Maintain short-term window of 2 interactions
            
        log_entry = f"[{datetime.now().isoformat()}] PHASE={phase.upper()} | SUCCESS={success} | TIME={duration:.3f}s | INPUT='{user_input}'\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def process_request(self, user_input: str) -> dict:
        start_time = time.time()
        
        # Execute the ORAA Cycle
        observation = self.observe(user_input)
        phase, confidence, reasoning = self.reason(observation)
        artifact_path = self.act(phase, user_input)
        
        duration = time.time() - start_time
        self.adapt(user_input, phase, True, duration)
        
        result = {
            "description": user_input,
            "phase": phase,
            "confidence": confidence,
            "reasoning": reasoning,
            "artifact": artifact_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save request data permanently to JSON storage
        with open(self.requests_file, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(result)
            f.seek(0)
            json.dump(data, f, indent=4)
            
        return result


# --- INTERACTIVE CLI INTERFACE ---
def main():
    agent = SDLCAutonomousAgent()
    
    print("=============================================")
    print("   Autonomous SDLC Agent & Tracker (Option B)")
    print("=============================================")

    while True:
        print("\n--- Main Menu ---")
        print("1. Process New Feature Request")
        print("2. View Stored Requests")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            desc = input("Enter feature description (min 10 chars): ").strip()
            if len(desc) < 10:
                print("Validation Error: Description must be at least 10 characters long.")
                continue
                
            print("\n[Agent executing Observe → Reason → Act → Adapt cycle...]")
            res = agent.process_request(desc)
            
            print(f" -> Phase Detected : {res['phase'].upper()} (Confidence: {res['confidence']})")
            print(f" -> Reasoning      : {res['reasoning']}")
            print(f" -> Artifact File  : {res['artifact']}")
            
        elif choice == "2":
            if agent.requests_file.exists():
                with open(agent.requests_file, "r", encoding="utf-8") as f:
                    reqs = json.load(f)
                print(f"\n--- Stored Feature Requests ({len(reqs)}) ---")
                for i, r in enumerate(reqs, 1):
                    print(f"{i}. [{r['phase'].upper()}] {r['description']}")
                    print(f"   File: {r['artifact']} | Time: {r['timestamp']}")
            else:
                print("\nNo requests found.")
                
        elif choice == "3":
            print("Exiting agent. Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 3.")

if __name__ == "__main__":
    main()