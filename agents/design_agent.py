import json
import re
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
You are an elite website design agent.

Your task is to create premium modern website design systems
based on the user request and planner output.

You intelligently decide:
- style family
- brand mood
- color palette
- typography
- spacing system
- radius system
- shadow style
- surface treatment
- motion personality
- asset direction

Rules:
- Return valid JSON only
- No markdown
- No explanations
- Use premium modern taste
"""


def generate_design(prompt, plan):

    design_prompt = f"""
User Request:
{prompt}

Planner Output:
{json.dumps(plan, indent=2)}

Return ONLY valid JSON in this format:

{{
  "style_family": "",
  "mode": "dark",
  "brand_mood": [],
  "palette": {{
    "primary": "",
    "secondary": "",
    "accent": "",
    "background": "",
    "surface": "",
    "text": ""
  }},
  "typography": {{
    "heading": "",
    "body": ""
  }},
  "spacing": [4,8,12,16,24,32],
  "radius": [8,12,20],
  "shadows": "",
  "surface_style": "",
  "motion": "",
  "assets": {{
    "icons": "",
    "hero": "",
    "background": ""
  }}
}}

Rules:
- Style must match business type
- If futuristic requested → premium futuristic style
- If law / finance → trustworthy premium style
- If ecommerce → conversion-focused modern style
- Return JSON only
"""

    response = llm(design_prompt, SYSTEM_PROMPT=SYSTEM_PROMPT)
    print(f"rseponse:{response}")

    try:
        match = re.search(r'\{[\s\S]*\}', response)

        if not match:
            raise ValueError("No JSON found")

        design = json.loads(match.group())

    except:
        design = {
            "style_family": "modern_clean",
            "mode": "dark",
            "brand_mood": ["premium", "clean"],
            "palette": {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "accent": "#06b6d4",
                "background": "#0f172a",
                "surface": "#111827",
                "text": "#ffffff"
            },
            "typography": {
                "heading": "Inter",
                "body": "Inter"
            },
            "spacing": [4, 8, 12, 16, 24, 32],
            "radius": [8, 12, 20],
            "shadows": "soft_glow",
            "surface_style": "clean_card",
            "motion": "smooth_premium",
            "assets": {
                "icons": "modern_outline",
                "hero": "premium_dashboard",
                "background": "gradient_mesh"
            }
        }

    return design


prompt = "Create a futuristic AI SaaS platform website for startups with premium dark mode, multiple pages, dashboard feel, smooth animations, and modern trust-building design"

plan = {
    "pages": {
        "marketing_pages": [
            "home",
            "features",
            "pricing",
            "about",
            "contact"
        ],
        "product_pages": [
            "dashboard",
            "analytics",
            "settings"
        ],
        "support_pages": [
            "faq",
            "privacy_policy",
            "terms_of_service"
        ]
    },
    "style": "futuristic premium modern dark",
    "layout": {
        "landing": [
            "navbar",
            "hero",
            "features_grid",
            "pricing_preview",
            "testimonial_strip",
            "footer"
        ],
        "dashboard": [
            "sidebar",
            "topbar",
            "stats_cards",
            "charts",
            "activity_feed"
        ]
    },
    "assets": [
        "3d_dashboard_mockup",
        "gradient_backgrounds",
        "modern_icons"
    ]
}

l = generate_design(prompt=prompt, plan=plan)

print(f" AI OUTPUT {json.dumps(l, indent=2)}")
