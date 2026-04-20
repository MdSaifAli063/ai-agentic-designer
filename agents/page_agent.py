import json
from ai_agentic_designer.agents.llm import llm
import re



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
- Use ALL planner pages
- Do not invent random pages
- Sections must match page purpose
"""


def generate_pages(prompt, plan):
    # flatten planner pages into one ordered list
    # NEW FLEXIBLE PAGE FLATTENING LOGIC

    pages_data = plan.get("page_groups", {})

    # fallback for old schema support
    if not pages_data:
        pages_data = plan.get("pages", {})

    ordered_pages = []

    # preferred category order if present
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

    # first add known priority groups
    for group in priority_order:
        if group in pages_data:
            ordered_pages.extend(pages_data[group])

    # then add any remaining dynamic groups
    for group, page_list in pages_data.items():
        if group not in priority_order:
            ordered_pages.extend(page_list)

    # normalize + remove duplicates
    seen = set()
    final_pages = []

    for p in ordered_pages:
        page = p.lower().replace(" ", "_").replace("-", "_")

        if page not in seen:
            seen.add(page)
            final_pages.append(page)

    page_prompt = f"""
User Request:
{prompt}

Planner Output:
{json.dumps(plan, indent=2)}

Required Pages:
{json.dumps(final_pages)}

Return ONLY valid JSON in this format:

{{
  "pages": [
    {{
      "name": "landing",
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
- Do not skip pages
- Do not add extra pages
- landing/home route = /
- other routes = /page_name
- marketing pages = public conversion pages
- product pages = dashboard/app pages
- support pages = help/legal/contact pages
- sections must fit page purpose
- valid JSON only
- Every page must include navbar + footer unless dashboard/app page
- Dashboard pages use sidebar + topbar
"""

    response = llm(page_prompt, SYSTEM_PROMPT=PAGE_SYSTEM_PROMPT)
    print("RAW LLM RESPONSE:", response)

    try:
        match = re.search(r'\{[\s\S]*\}', response)
        if not match:
            raise ValueError("No JSON found")

        pages = json.loads(match.group())

    except Exception as e:
      raise ValueError(f"Failed to parse page agent JSON output: {str(e)}")
    return pages



plan = {
    'pages': {'marketing_pages': ['Home', 'About Us', 'Services', 'Testimonials', 'Blog'], 'product_pages': ['Practice Areas', 'Legal Guides', 'Case Studies'], 'support_pages': ['Contact Us', 'FAQ', 'Privacy Policy', 'Terms of Service']},
    "style": "modern ai saas",
    "layout": {},
    "assets": []
  }
prompt = "law firm"

l = generate_pages(prompt=prompt, plan=plan )
print(f"ai output:{l}")



