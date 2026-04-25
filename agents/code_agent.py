import json
import re
from ai_agentic_designer.agents.llm import llm_gemini


SYSTEM_PROMPT = """
You are a senior frontend engineer.

You generate clean production-ready React + Tailwind CSS code.

Expert in:
- React
- Tailwind CSS
- React Router

Rules:
- Use provided JSON exactly
- Respect sections and routes
- Build only ONE page component at a time
- Return valid JSX code only
- No markdown
- No explanations
"""


def generate_code(state):

    prompt = state.get("prompt", "")
    design = state.get("design", {})
    ui = state.get("ui", {})

    ui_pages = ui.get("pages", [])

    files = {}

    # fallback if no pages
    if not ui_pages:
        return {
            "files": {
                "App.jsx": """
export default function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white">
      No UI pages generated
    </div>
  )
}
"""
            }
        }

    # -----------------------------------------
    # Generate ONE PAGE AT A TIME
    # -----------------------------------------
    for page in ui_pages:

        page_name = page.get("name", "Page")
        route = page.get("route", "/")
        sections = page.get("ui_sections", [])

        component_name = "".join(word.capitalize() for word in page_name.split("_"))

        code_prompt = f"""
User Request:
{prompt}

Design JSON:
{json.dumps(design, indent=2)}

Current Page JSON:
{json.dumps(page, indent=2)}

Generate React + Tailwind JSX component.

Requirements:
- Component name = {component_name}
- Use sections exactly as given
- Use premium styling
- Use dark mode if provided
- Use reusable JSX structure
- Keep code concise
- Export default component
- Return JSX only
"""

        response = llm_gemini(code_prompt, SYSTEM_PROMPT=SYSTEM_PROMPT)

        # remove markdown fences if model adds them
        response = re.sub(r"```jsx|```javascript|```js|```", "", response).strip()

        files[f"{component_name}.jsx"] = response

    # -----------------------------------------
    # Generate App.jsx Router Shell
    # -----------------------------------------
    imports = []
    routes_code = []

    for page in ui_pages:
        page_name = page.get("name", "page")
        route = page.get("route", "/")

        component_name = "".join(word.capitalize() for word in page_name.split("_"))

        imports.append(
            f'import {component_name} from "./pages/{component_name}";'
        )

        routes_code.append(
            f'<Route path="{route}" element={{<{component_name} />}} />'
        )

    app_code = f"""
import {{ BrowserRouter, Routes, Route, Link }} from "react-router-dom";
{chr(10).join(imports)}

export default function App() {{
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-black text-white">
        <nav className="flex gap-6 px-8 py-4 border-b border-white/10">
          {"".join([f'<Link to="{p.get("route","/")}" className="hover:text-cyan-400">{p.get("name","page").replace("_"," ").title()}</Link>' for p in ui_pages])}
        </nav>

        <Routes>
          {chr(10).join(routes_code)}
        </Routes>
      </div>
    </BrowserRouter>
  )
}}
"""

    files["App.jsx"] = app_code

    return {
        "files": files
    }