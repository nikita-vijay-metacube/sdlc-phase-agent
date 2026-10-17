import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class DocumentGenerator:
    """Generates organized SDLC phase documents from templates."""

    TEMPLATES = {
        "requirements": """# Requirements Document

Feature: {title}
Date: {date}
Project: {project} | Client: {client}

## Description
{description}

## Basic Requirements
{generated_content}

## Next Steps
- Review requirements with stakeholders.
- Obtain sign-off and proceed to the Design phase.
""",
        "design": """# System Design Outline

Feature: {title}
Date: {date}
Project: {project} | Client: {client}

## Overview
{description}

## Architecture & Component Design
{generated_content}

## Next Steps
- Review architecture with senior developers.
- Prepare implementation tasks and task breakdown.
""",
        "implementation": """# Implementation Plan & Task List

Feature: {title}
Date: {date}
Project: {project} | Client: {client}

## Feature Summary
{description}

## Implementation Checklist
{generated_content}

## Next Steps
- Begin development in feature branch.
- Submit pull request for peer code review.
""",
        "testing": """# Test Plan & Specifications

Feature: {title}
Date: {date}
Project: {project} | Client: {client}

## Target Feature
{description}

## Test Cases
{generated_content}

## Next Steps
- Execute test suite and log any bugs.
- Obtain QA verification before deployment.
""",
        "deployment": """# Deployment Checklist & Release Notes

Feature: {title}
Date: {date}
Project: {project} | Client: {client}

## Release Overview
{description}

## Deployment Steps
{generated_content}

## Next Steps
- Verify production deployment health and logs.
- Notify client/stakeholders of release completion.
"""
    }

    def __init__(self, base_artifacts_dir: str = "artifacts"):
        self.base_dir = Path(base_artifacts_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Creates organized subdirectories for each phase under artifacts/."""
        phases = ["requirements", "design", "implementation", "testing", "deployment"]
        for phase in phases:
            (self.base_dir / phase).mkdir(parents=True, exist_ok=True)

    def generate_content_for_phase(self, phase: str, description: str, llm_model=None) -> str:
        """Generates phase-specific structured content using LLM or structured heuristics."""
        if llm_model:
            try:
                prompt = (
                    f"Generate bullet points for a software document in the '{phase}' phase "
                    f"based on this request: '{description}'. Keep it concise, professional, and actionable."
                )
                response = llm_model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass

        # Structured heuristic fallbacks
        heuristics = {
            "requirements": (
                "- Functional Requirement 1: Support user actions for " + description + "\n"
                "- Functional Requirement 2: Ensure data validation and response error handling.\n"
                "- Non-Functional Requirement: Response time must be under 200ms."
            ),
            "design": (
                "- Component 1: User Interface / API Endpoint Controller\n"
                "- Component 2: Application Service Layer & Validation Logic\n"
                "- Component 3: Database Data Access Model & Storage"
            ),
            "implementation": (
                "- Task 1: Setup data schemas and models.\n"
                "- Task 2: Implement core business logic functions.\n"
                "- Task 3: Create unit tests and API route handlers."
            ),
            "testing": (
                "- Test Case 1: Verify valid input processing.\n"
                "- Test Case 2: Verify error message on invalid input.\n"
                "- Test Case 3: Verify end-to-end integration flow."
            ),
            "deployment": (
                "- Step 1: Run automated test suite in CI pipeline.\n"
                "- Step 2: Deploy database migrations and updated service build.\n"
                "- Step 3: Perform post-deployment smoke test."
            )
        }
        return heuristics.get(phase, "- Step 1: Review request details.\n- Step 2: Proceed with phase tasks.")

    def create_document(self, request_data: Dict[str, Any], llm_model=None) -> str:
        """Loads template, substitutes variables, and saves file to organized directory."""
        phase = request_data.get("phase", "requirements").lower()
        if phase not in self.TEMPLATES:
            phase = "requirements"

        template = self.TEMPLATES[phase]
        today_str = datetime.now().strftime("%Y-%m-%d")
        title = request_data.get("description", "Feature")[:30] + "..."

        generated_content = self.generate_content_for_phase(phase, request_data.get("description", ""), llm_model)

        document_text = template.format(
            title=title,
            date=today_str,
            project=request_data.get("project", "General"),
            client=request_data.get("client", "Internal"),
            description=request_data.get("description", ""),
            generated_content=generated_content
        )

        filename = f"doc_{request_data.get('id', 'req')}_{phase}.md"
        output_file = self.base_dir / phase / filename

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(document_text)

        return str(output_file)