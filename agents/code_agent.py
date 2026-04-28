import asyncio
import json
import logging
import re

from ai_agentic_designer.agents.llm import CODE_MODEL, invoke_text_model_async


logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are a senior frontend engineer building premium production-grade React + Tailwind websites.

You write:
- clean React function components
- premium modern layouts
- motion-aware section structure
- coherent multi-page visual systems
- concise, readable JSX

Quality rules:
- Return valid JSX only
- No markdown
- No explanations
- Export a default component
- Build a polished visual hierarchy
- Match the supplied design system exactly
- Keep components self-contained
- Prefer a minimal React + Tailwind runtime with no required external packages unless absolutely necessary
- Add animation-ready structure inspired by GSAP, Framer Motion, and React Three Fiber patterns
- If the concept strongly benefits from advanced animation, introduce it carefully and only when the component still remains buildable
- Avoid placeholder lorem ipsum
- Keep sections purposeful and visually distinct
"""


def _strip_code_fences(code: str) -> str:
    return re.sub(r"```(?:jsx|javascript|js)?|```", "", code).strip()


def _component_name(page_name: str) -> str:
    return "".join(word.capitalize() for word in page_name.split("_")) or "Page"


def _normalize_page_specs(state: dict) -> list[dict]:
    page_map: dict[str, dict] = {}

    for page in state.get("pages", {}).get("pages", []):
        page_name = page.get("name")
        if not page_name:
            continue
        page_map[page_name] = {
            "name": page_name,
            "route": page.get("route", "/"),
            "type": page.get("type", "marketing"),
            "goal": page.get("goal", ""),
            "sections": page.get("sections", []),
            "ui_sections": [],
        }

    for page in state.get("ui", {}).get("pages", []):
        page_name = page.get("name")
        if not page_name:
            continue

        if page_name not in page_map:
            page_map[page_name] = {
                "name": page_name,
                "route": page.get("route", "/"),
                "type": "marketing",
                "goal": "",
                "sections": [],
                "ui_sections": page.get("ui_sections", []),
            }
        else:
            page_map[page_name]["ui_sections"] = page.get("ui_sections", [])

    return list(page_map.values())


def _fallback_component(page: dict, error: str) -> str:
    component_name = _component_name(page.get("name", "page"))
    title = page.get("name", "page").replace("_", " ").title()
    goal = page.get("goal", "Display the page content.")

    return f"""
export default function {component_name}() {{
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 px-6 py-16">
      <div className="mx-auto max-w-5xl rounded-3xl border border-white/10 bg-white/5 p-10 shadow-2xl shadow-cyan-500/10">
        <p className="text-xs uppercase tracking-[0.4em] text-cyan-300">Fallback Render</p>
        <h1 className="mt-4 text-4xl font-semibold">{title}</h1>
        <p className="mt-4 max-w-2xl text-slate-300">{goal}</p>
        <div className="mt-10 rounded-2xl border border-amber-400/30 bg-amber-400/10 p-5 text-sm text-amber-100">
          Code generation recovered from an error for this page.
        </div>
        <pre className="mt-6 overflow-x-auto rounded-2xl bg-black/40 p-5 text-xs text-slate-300">{json.dumps(error)}</pre>
      </div>
    </main>
  )
}}
""".strip()


def _build_app_shell(page_specs: list[dict], design: dict) -> str:
    imports = []
    route_entries = []
    nav_links = []

    for page in page_specs:
        component_name = _component_name(page["name"])
        route = page.get("route", "/")
        label = page["name"].replace("_", " ").title()
        imports.append(f'import {component_name} from "./pages/{component_name}";')
        route_entries.append(f'  "{route}": {component_name},')
        nav_links.append(
            "{ route: "
            + json.dumps(route)
            + f', label: "{label}"'
            + " }"
        )

    background = design.get("palette", {}).get("background", "#020617")
    text = design.get("palette", {}).get("text", "#f8fafc")
    accent = design.get("palette", {}).get("accent", "#22d3ee")

    active_class = (
        'route === item.route '
        '? "rounded-full px-4 py-2 transition bg-white/12 text-white" '
        ': "rounded-full px-4 py-2 transition hover:bg-white/8 hover:text-white"'
    )

    return f"""
import {{ useEffect, useState }} from "react";
{chr(10).join(imports)}

const routes = {{
{chr(10).join(route_entries)}
}};

const navigation = [{", ".join(nav_links)}];

function getCurrentRoute() {{
  const hash = window.location.hash.replace(/^#/, "") || "/";
  return routes[hash] ? hash : "/";
}}

export default function App() {{
  const [route, setRoute] = useState(getCurrentRoute());

  useEffect(() => {{
    const handleHashChange = () => setRoute(getCurrentRoute());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }}, []);

  const ActivePage = routes[route] || routes["/"];

  return (
    <div className="min-h-screen" style={{{{ background: "{background}", color: "{text}" }}}}>
      <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <a href="#/" className="text-sm font-semibold uppercase tracking-[0.35em]" style={{{{ color: "{accent}" }}}}>
            Agentic UI
          </a>
          <nav className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
            {{navigation.map((item) => (
              <a
                key={{item.route}}
                href={{`#${{item.route}}`}}
                className={{{active_class}}}
              >
                {{item.label}}
              </a>
            ))}}
          </nav>
        </div>
      </header>
      <ActivePage />
    </div>
  );
}}
""".strip()


async def _generate_single_page(
    prompt: str,
    design: dict,
    page: dict,
    site_context: list[dict],
) -> tuple[str, str]:
    component_name = _component_name(page.get("name", "page"))
    print(f"[code] {component_name}: generation started", flush=True)

    code_prompt = f"""
User Request:
{prompt}

Shared Design System:
{json.dumps(design, indent=2)}

Current Page:
{json.dumps(page, indent=2)}

Other Site Pages:
{json.dumps(site_context, indent=2)}

Generate a premium React + Tailwind component for this page.

Implementation requirements:
- Component name must be {component_name}
- Export default component
- Use the supplied ui_sections exactly and in order
- Make the design visually premium, modern, and polished
- Create strong motion-ready composition inspired by GSAP, Framer Motion, and React Three Fiber
- Use tasteful gradients, layered backgrounds, glass, grids, cards, and strong typography when appropriate
- Do not require external assets
- Keep the component self-contained
- Ensure the page feels connected to the other site pages through tone and navigation cues
- Keep JSX valid and production-lean
"""

    response = await invoke_text_model_async(
        prompt=code_prompt,
        system_prompt=SYSTEM_PROMPT,
        model_name=CODE_MODEL,
        temperature=0.7,
    )

    code = _strip_code_fences(response)
    if "export default function" not in code and "export default" not in code:
        raise ValueError(f"Model did not return a default export for {component_name}")

    print(f"[code] {component_name}: generation completed", flush=True)
    return f"{component_name}.jsx", code


def generate_code(state: dict) -> dict:
    prompt = state.get("prompt", "")
    design = state.get("design", {})
    page_specs = _normalize_page_specs(state)

    if not page_specs:
        return {
            "files": {
                "App.jsx": """
export default function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
      No UI pages generated
    </div>
  )
}
""".strip()
            }
        }

    async def _generate_all_pages() -> dict[str, str]:
        print(f"[code] parallel generation: {len(page_specs)} page tasks", flush=True)
        tasks = [
            _generate_single_page(
                prompt=prompt,
                design=design,
                page=page,
                site_context=[
                    {
                        "name": sibling["name"],
                        "route": sibling.get("route", "/"),
                        "type": sibling.get("type", "marketing"),
                    }
                    for sibling in page_specs
                    if sibling["name"] != page["name"]
                ],
            )
            for page in page_specs
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        files: dict[str, str] = {}

        for page, result in zip(page_specs, results):
            file_name = f"{_component_name(page['name'])}.jsx"

            if isinstance(result, Exception):
                print(f"[code] {file_name}: fallback generated after error", flush=True)
                logger.error(
                    "Page generation failed for %s: %s",
                    page["name"],
                    result,
                    exc_info=result,
                )
                files[file_name] = _fallback_component(page, str(result))
                continue

            generated_file_name, code = result
            files[generated_file_name] = code

        return files

    files = asyncio.run(_generate_all_pages())
    print("[code] app shell: building", flush=True)
    files["App.jsx"] = _build_app_shell(page_specs=page_specs, design=design)
    print("[code] app shell: completed", flush=True)

    return {"files": files}
