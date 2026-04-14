from fastapi import FastAPI
from pydantic import BaseModel

from agents.planner_agent import planner

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "Agentic UI Designer Running"}


@app.post("/generate")
def generate(request: PromptRequest):

    result = planner(request.prompt)

    return {
        "result": result
    }
