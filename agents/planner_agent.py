import json
from ai_agentic_designer.agents.llm import llm


SYSTEM_PROMPT = """
    You are an elite website planning agent for autonomous website generation.

    Your job is to convert user requests into structured website plans.

    Infer intelligently:
    - business type
    - target audience
    - required pages
    - page categories
    - style direction
    - realistic navigation structure
    - logical section flow
    - required assets

    Rules:
    - Always return valid JSON only
    - No markdown
    - No explanations
    - Use practical page names
    - Use snake_case naming
    - Include auth/support pages when needed
    - Choose style based on prompt context
    - Optimize for real modern websites
    """


def planner(prompt):

    planning_prompt = f"""
    User Request:
    {prompt}
    you are just an elite planning agent 

     
    Return ONLY valid JSON in this Example  format
    don't rely on the example you can extend it acccording what user wants:

    {{
        "pages": {{
                    "marketing_pages": [...],
                    "product_pages": [...],
                    "support_pages": [...]
                    }},
        "style": "",
        "layout": {{
                    "dashboard": [...],
                    "landing": [...],
                    "pricing": [...]
                    }},
        "assets": []
    }}

    Rules:
    - include essential pages that are required
    - pages must logically match user request
    - include auth pages if needed
    - use futuristic style if requested
    - no markdown
    - no explanation

        
    """

    response = llm(planning_prompt, SYSTEM_PROMPT=SYSTEM_PROMPT)
    print(f" response {response}")

    try:
        plan = json.loads(response)
        # print(f"plan{plan}")
    except Exception as e:
        print("Planner parse failed:", e)

    return plan

prompt = " portfolio for ML engineer"

l = planner(prompt=prompt)
print(f"ai output:{l}")



# so we will build the tools today then afterwards we will integrate it with the agents ok so now first focus will tools and not custom tools but external tools either via api or througn langraph mcp 


