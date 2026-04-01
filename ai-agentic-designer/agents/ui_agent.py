import requests

SYSTEM_PROMPT = """

You are a helpful assistant that generates code for building user interfaces based on user requirements. 
You will
"""

def llm(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen3:8b",
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }

    response = requests.post(url, json=payload)

    data = response.json()

    return data.get('response', '')



