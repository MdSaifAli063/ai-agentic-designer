import requests
import json

SYSTEM_PROMPT = """
You are an AI UI/UX design system that helps generate structured outputs
for building websites using multi-agent architecture.
"""

def llm(prompt, SYSTEM_PROMPT=True):

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen3:8b",
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }

    response = requests.post(url, json=payload)

    data = response.json()

    return data.get("response", "")
