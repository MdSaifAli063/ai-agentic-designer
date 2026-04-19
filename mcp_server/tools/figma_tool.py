import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_KEY")  # ← load from .env

async def get_remote_figma_tools():
    if not FIGMA_API_KEY:
        raise ValueError("FIGMA_API_KEY is not set in .env")
    if not FIGMA_FILE_KEY:
        raise ValueError("FIGMA_FILE_KEY is not set in .env")

    client = MultiServerMCPClient({
        "figma": {
            "command": "npx",
            "args": [
                "-y",
                "figma-developer-mcp",
                f"--figma-api-key={FIGMA_API_KEY}",
                "--stdio"
            ],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()

    return {
        "client": client,
        "tools": tools,
    }


if __name__ == "__main__":
    async def main():
        result = await get_remote_figma_tools()
        tools = result["tools"]

        get_data_tool = next(t for t in tools if t.name == "get_figma_data")

        response = await get_data_tool.ainvoke({
            "fileKey": FIGMA_FILE_KEY,
        })

        print(response)

    asyncio.run(main())