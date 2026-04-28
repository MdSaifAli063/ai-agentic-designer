import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_agentic_designer.agents.graphs import run_graph


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

project_root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
module_env = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=project_root_env)
load_dotenv(dotenv_path=module_env, override=False)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str


@app.post("/generate")
def generate(request: PromptRequest):
    try:
        result = run_graph(request.prompt)
        return {"result": result}
    except Exception as exc:
        logger.exception("Generation request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


frontend_dist = os.path.join(os.path.dirname(__file__), "frontend/dist")
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    index_file = os.path.join(frontend_dist, "index.html")

    if not os.path.isfile(index_file):
        raise HTTPException(status_code=404, detail="Frontend build not found")

    return FileResponse(index_file)
