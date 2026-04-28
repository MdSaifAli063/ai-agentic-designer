import json
import logging
import os
from typing import Any

from pydantic import BaseModel, Field

from ai_agentic_designer.agents.llm import PLANNING_MODEL, invoke_structured_model


logger = logging.getLogger(__name__)


def _dump_model(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


class PageGroups(BaseModel):
    marketing_pages: list[str] = Field(default_factory=list)
    service_pages: list[str] = Field(default_factory=list)
    catalog_pages: list[str] = Field(default_factory=list)
    auth_pages: list[str] = Field(default_factory=list)
    dashboard_pages: list[str] = Field(default_factory=list)
    resource_pages: list[str] = Field(default_factory=list)
    docs_pages: list[str] = Field(default_factory=list)
    support_pages: list[str] = Field(default_factory=list)
    legal_pages: list[str] = Field(default_factory=list)


class SitePlan(BaseModel):
    page_groups: PageGroups
    style: str
    layout: dict[str, list[str]] = Field(default_factory=dict)
    assets: list[str] = Field(default_factory=list)


class Palette(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text: str


class Typography(BaseModel):
    heading: str
    body: str


class AssetDirection(BaseModel):
    icons: str
    hero: str
    background: str


class DesignSystem(BaseModel):
    style_family: str
    mode: str
    brand_mood: list[str] = Field(default_factory=list)
    palette: Palette
    typography: Typography
    spacing: list[int] = Field(default_factory=list)
    radius: list[int] = Field(default_factory=list)
    shadows: str
    surface_style: str
    motion: str
    assets: AssetDirection


class UISection(BaseModel):
    type: str
    variant: str
    layout: str
    motion: str


class PlannedPage(BaseModel):
    name: str
    route: str
    type: str
    goal: str
    sections: list[str] = Field(default_factory=list)
    ui_sections: list[UISection] = Field(default_factory=list)


class SiteSpecification(BaseModel):
    plan: SitePlan
    design: DesignSystem
    pages: list[PlannedPage] = Field(default_factory=list)


SYSTEM_PROMPT = """
You are the master website planning agent for a production-grade AI website generator.

You convert a user request into a complete premium multi-page website specification.

Requirements:
- Think like a senior product designer, creative director, UX architect, and frontend lead.
- Produce realistic information architecture for modern websites.
- Make the output premium, coherent, and buildable.
- Use dark mode only if it matches the request or improves the concept.
- Prefer premium modern layouts, bold visual direction, strong hierarchy, and motion-aware sections.
- Every page must have a clear purpose and a logical route.
- Every page must include UI sections that a frontend engineer can directly implement.
- Use section variants that can support premium animation with GSAP, Framer Motion, and React Three Fiber when appropriate.
- Keep the page count practical for an MVP, usually 3 to 8 pages.
- Use snake_case names for page names and section types.
- Home page route must be "/".
- Other routes must begin with "/".
"""


def _normalize_page_name(name: str) -> str:
    return str(name).strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_route(route: str, page_name: str) -> str:
    cleaned = str(route).strip()
    if not cleaned:
        return "/" if page_name in {"home", "landing"} else f"/{page_name}"
    if cleaned == "/":
        return "/"
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned


def _normalize_sections(sections: list[str]) -> list[str]:
    normalized = []
    seen = set()

    for section in sections:
        section_name = _normalize_page_name(section)
        if section_name and section_name not in seen:
            seen.add(section_name)
            normalized.append(section_name)

    return normalized[:7]


def _normalize_site_spec(spec: SiteSpecification) -> SiteSpecification:
    route_seen = set()
    normalized_pages: list[PlannedPage] = []

    for raw_page in spec.pages[:8]:
        page_name = _normalize_page_name(raw_page.name)
        if not page_name:
            continue

        route = _normalize_route(raw_page.route, page_name)
        if route in route_seen:
            continue

        route_seen.add(route)
        normalized_sections = _normalize_sections(raw_page.sections)

        normalized_ui_sections = []
        for ui_section in raw_page.ui_sections:
            section_type = _normalize_page_name(ui_section.type)
            if section_type not in normalized_sections:
                continue

            normalized_ui_sections.append(
                UISection(
                    type=section_type,
                    variant=str(ui_section.variant).strip() or "premium_default",
                    layout=str(ui_section.layout).strip() or "stack",
                    motion=str(ui_section.motion).strip() or "fade_up",
                )
            )

        missing_ui_sections = [
            section
            for section in normalized_sections
            if section not in {item.type for item in normalized_ui_sections}
        ]

        for section in missing_ui_sections:
            normalized_ui_sections.append(
                UISection(
                    type=section,
                    variant="premium_default",
                    layout="stack",
                    motion="fade_up",
                )
            )

        normalized_pages.append(
            PlannedPage(
                name=page_name,
                route="/" if page_name in {"home", "landing"} else route,
                type=str(raw_page.type).strip() or "marketing",
                goal=str(raw_page.goal).strip() or "present content clearly",
                sections=normalized_sections or ["navbar", "hero", "content", "footer"],
                ui_sections=normalized_ui_sections,
            )
        )

    if not normalized_pages:
        normalized_pages = [
            PlannedPage(
                name="home",
                route="/",
                type="marketing",
                goal="convert visitors with a premium landing experience",
                sections=["navbar", "hero", "features", "cta", "footer"],
                ui_sections=[
                    UISection(
                        type="navbar",
                        variant="glass_sticky",
                        layout="horizontal",
                        motion="fade_down",
                    ),
                    UISection(
                        type="hero",
                        variant="split_with_3d_visual",
                        layout="two_column",
                        motion="stagger_reveal",
                    ),
                    UISection(
                        type="features",
                        variant="bento_grid",
                        layout="grid",
                        motion="cascade_cards",
                    ),
                    UISection(
                        type="cta",
                        variant="centered_glow_panel",
                        layout="stack",
                        motion="scale_in",
                    ),
                    UISection(
                        type="footer",
                        variant="multi_column",
                        layout="grid",
                        motion="fade_up",
                    ),
                ],
            )
        ]

    spec.pages = normalized_pages
    return spec


def _site_spec_to_state(spec: SiteSpecification) -> dict[str, Any]:
    spec = _normalize_site_spec(spec)

    pages_payload = {
        "pages": [
            {
                "name": page.name,
                "route": page.route,
                "type": page.type,
                "goal": page.goal,
                "sections": page.sections,
            }
            for page in spec.pages
        ]
    }

    ui_payload = {
        "pages": [
            {
                "name": page.name,
                "route": page.route,
                "ui_sections": [_dump_model(section) for section in page.ui_sections],
            }
            for page in spec.pages
        ]
    }

    return {
        "plan": _dump_model(spec.plan),
        "design": _dump_model(spec.design),
        "pages": pages_payload,
        "ui": ui_payload,
    }


def planner(prompt: str) -> dict[str, Any]:
    planning_prompt = f"""
User Request:
{prompt}

Return a complete website specification with:
- plan
- design
- pages

Rules:
- Keep the website practical but premium.
- Every page must include both sections and ui_sections.
- ui_sections must align one-to-one with the page sections whenever possible.
- Favor premium animation-ready variants.
- Include shared navigation and footer patterns across public pages.
- For SaaS, startup, AI, gaming, or futuristic products, bias toward bold motion and high-contrast premium composition.
- For trust-heavy categories like finance, law, healthcare, or B2B enterprise, keep the design more restrained and trustworthy.
"""

    spec = invoke_structured_model(
        prompt=planning_prompt,
        schema=SiteSpecification,
        system_prompt=SYSTEM_PROMPT,
        model_name=PLANNING_MODEL,
        temperature=0.3,
        max_attempts=3,
    )

    logger.info("Merged planning spec generated with %s pages", len(spec.pages))
    state_payload = _site_spec_to_state(spec)

    if os.getenv("PRINT_AGENT_JSON", "false").lower() in {"1", "true", "yes", "on"}:
        print("[planner] validated json output:", flush=True)
        print(json.dumps(state_payload, indent=2), flush=True)

    return state_payload
