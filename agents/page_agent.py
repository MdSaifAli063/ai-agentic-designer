import json
import re
from ai_agentic_designer.agents.llm import llm_groq


PAGE_SYSTEM_PROMPT = """
You are an elite website page composition agent.

Your task is to convert planner output into structured multipage website blueprints.

You decide:
- page purpose
- route path
- page category
- section hierarchy
- logical user flow

Rules:
- Return valid JSON only
- No markdown
- No explanations
- Use snake_case names
- Do not invent random pages
- Sections must match page purpose
- Keep output concise
"""


def generate_pages(prompt, plan):
    """
    Converts planner output into structured pages JSON
    """

    # -----------------------------
    # Load page groups safely
    # -----------------------------
    pages_data = plan.get("page_groups", {})

    # fallback older schema
    if not pages_data:
        pages_data = plan.get("pages", {})

    # -----------------------------
    # Preferred ordering
    # -----------------------------
    priority_order = [
        "marketing_pages",
        "service_pages",
        "catalog_pages",
        "auth_pages",
        "app_pages",
        "dashboard_pages",
        "resource_pages",
        "docs_pages",
        "support_pages",
        "legal_pages"
    ]

    ordered_pages = []

    # known groups first
    for group in priority_order:
        if group in pages_data:
            ordered_pages.extend(pages_data[group])

    # dynamic groups later
    for group, page_list in pages_data.items():
        if group not in priority_order:
            ordered_pages.extend(page_list)

    # -----------------------------
    # Normalize + dedupe
    # -----------------------------
    seen = set()
    final_pages = []

    for p in ordered_pages:
        page = str(p).lower().replace(" ", "_").replace("-", "_").strip()

        if page and page not in seen:
            seen.add(page)
            final_pages.append(page)

    # -----------------------------
    # Limit for speed / MVP
    # -----------------------------
    final_pages = final_pages[:8]

    # fallback pages if planner empty
    if not final_pages:
        final_pages = [
            "home",
            "about",
            "services",
            "pricing",
            "contact"
        ]

    # -----------------------------
    # Compact planner context
    # -----------------------------
    planner_context = {
        "style": plan.get("style", ""),
        "layout": plan.get("layout", {}),
        "assets": plan.get("assets", [])
    }

    # -----------------------------
    # LLM Prompt
    # -----------------------------
    page_prompt = f"""
User Request:
{prompt}

Planner Context:
{json.dumps(planner_context, indent=2)}

Required Pages:
{json.dumps(final_pages)}

Return ONLY valid JSON in this format:

{{
  "pages": [
    {{
      "name": "home",
      "route": "/",
      "type": "marketing",
      "goal": "convert visitors",
      "sections": [
        "navbar",
        "hero",
        "features",
        "cta",
        "footer"
      ]
    }}
  ]
}}

Rules:
- Use ALL required pages
- Do not add extra pages
- home or landing route = /
- other routes = /page_name
- Every page max 5 sections
- Marketing pages = navbar + hero + content + footer
- Support pages = navbar + content + footer
- Dashboard/App pages = sidebar + topbar + content
- Legal pages = navbar + policy_content + footer
- Valid JSON only
"""

    response = llm_groq(page_prompt, SYSTEM_PROMPT=PAGE_SYSTEM_PROMPT)

    try:
        match = re.search(r'\{[\s\S]*\}', response)
        if not match:
            raise ValueError("No JSON found")

        pages = json.loads(match.group())

    except Exception as e:
      raise ValueError(f"Failed to parse page agent JSON output: {str(e)}")
    return pages



