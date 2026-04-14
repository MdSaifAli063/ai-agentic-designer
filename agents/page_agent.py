import json
from ai_agentic_designer.agents.llm import llm


def generate_pages(prompt):

  page_prompt = f"""
  
  Generate website pages based on the user request.

  user request: {prompt}
 


  Return JSON:
  {{
    "pages": [
      {{
        "name": "home",
        "content": "..."
      }},
      ...
    ]
  }}
  """

  response = llm(page_prompt)

  try:
    pages = json.loads(response)
  except:
    pages = {"pages":["home"]}


  return pages 