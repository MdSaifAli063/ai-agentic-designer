import json
import re
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
You are a senior frontend engineer.

You generate production-ready React + Tailwind CSS code.

Expert in:
- React
- Tailwind CSS
- React Router
- Framer Motion
- GSAP

Rules:
- Use provided JSON exactly
- Do not invent random pages
- Respect layout + sections
- Build one clean App.jsx file
- Use React Router for multi-page structure
- Return code only
- No markdown
"""


def generate_code(state):

    prompt = state.get("prompt", "")
    pages = state.get("pages", {})
    design = state.get("design", {})
    ui = state.get("ui", {})

    code_prompt = f"""
User Request:
{prompt}

Pages JSON:
{json.dumps(pages, indent=2)}

Design JSON:
{json.dumps(design, indent=2)}

UI JSON:
{json.dumps(ui, indent=2)}

Generate a clean React + Tailwind App.jsx file.

Requirements:
- Use React Router
- Build pages logically
- Navbar links must connect pages
- Use design colors
- Use reusable components where possible
- Add subtle Framer Motion animations
- Return code only
"""

    response = llm(code_prompt, SYSTEM_PROMPT=SYSTEM_PROMPT)

    return {
        "files": {
            "App.jsx": response
        }
    }