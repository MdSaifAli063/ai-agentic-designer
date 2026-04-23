from fastapi import FastAPI
from pydantic import BaseModel

from ai_agentic_designer.agents.graphs import run_graph

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "Agentic UI Designer Running"}


@app.post("/generate")
def generate(request: PromptRequest):

    result = run_graph(request.prompt)

    return {
        "result": result
    }