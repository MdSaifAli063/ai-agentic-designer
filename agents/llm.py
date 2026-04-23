import requests


def llm(prompt, SYSTEM_PROMPT=None):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen3:8b",
        "prompt": prompt,
        "system": SYSTEM_PROMPT or "",
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()