from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class ToolRequest(BaseModel):
    tool_name: str
    input: dict


@app.get("/")
def root():
    return {"message": "agentic designer tools server is running"}


@app.post("/run_tools")
def run_tools(request: ToolRequest):
    return {
        "tool": request.tool_name,
        "status": "success",
        "input": request.input
    }


