import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()





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

    response = requests.post(url, json=payload, timeout=420)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()




def llm_groq(prompt, SYSTEM_PROMPT=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
    }
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 8192
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if "choices" not in data:
        if data.get("error", {}).get("code") == "rate_limit_exceeded":
            print("Rate limit hit, waiting 40 seconds...")
            time.sleep(40)  # wait and retry once
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
        else:
            print("Groq error:", data)
            raise Exception(f"Groq error: {data}")

    return data["choices"][0]["message"]["content"]