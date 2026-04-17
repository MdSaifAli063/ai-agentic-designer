import json
from ai_agentic_designer.agents.llm import llm
import re


def generate_pages(prompt, plan):

  page_prompt = f"""
    You are a professional website page generator.

    Your task:
    Generate MULTIPLE website pages based on the user request and planner output.

    User Request:
    {prompt}

    Planner Output:
    {json.dumps(plan, indent=2)}     

    STRICT RULES:
    - Use ALL pages from planner output
    - Do NOT skip any page
    - Do NOT add extra pages
    - Generate content for EACH page
    - Each page MUST include a navbar with links to ALL pages
    - Use routes like /home, /about, /features, etc.
    - Output MUST be valid JSON only
    - Do NOT include explanations, text, or comments

    Return ONLY this format:

    {{
      "pages": [
        {{
          "name": "home",
          "content": "<html content>"
        }}
      ]
    }}
    """

  response = llm(page_prompt)

  try:
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        pages = json.loads(match.group())
    else:
        raise ValueError("No JSON found")
  except:
      pages = {
          "pages": [
              {"name": p, "content": f"<div>{p} page</div>"}
              for p in plan.get("pages", ["home"])
          ]
      }


  return pages 