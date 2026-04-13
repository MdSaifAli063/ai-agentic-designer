import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_KEY")


@tool
def get_figma_file():
    """
    Get figma file content
    """

    url = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}"

    headers = {
        "X-Figma-Token": FIGMA_API_KEY
    }

    response = requests.get(url, headers=headers)

    return response.json()


@tool
def create_figma_frame(name: str):
    """
    Create frame (placeholder logic)
    """

    return {
        "status": "frame_created",
        "name": name
    }



@tool
def create_ui_frames(layout: list):
    """
    Create UI frames in figma
    """

    frames = []

    y_position = 0

    for component in layout:
        frames.append({
            "name": component,
            "x": 0,
            "y": y_position,
            "width": 1440,
            "height": 200
        })

        y_position += 220

    return {
        "frames": frames
    }