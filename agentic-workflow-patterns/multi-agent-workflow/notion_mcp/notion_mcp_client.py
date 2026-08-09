import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")
PARENT_PAGE_ID = os.getenv("PARENT_PAGE_ID")


def split_into_chunks(text: str, chunk_size: int = 1900) -> list[str]:
    """Split text into chunks of max chunk_size characters."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


async def create_page(title: str, content: str) -> str:
    missing = [
        name
        for name, value in {
            "MCP_SERVER_URL": MCP_SERVER_URL,
            "MCP_AUTH_TOKEN": MCP_AUTH_TOKEN,
            "PARENT_PAGE_ID": PARENT_PAGE_ID,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing Notion MCP configuration: {', '.join(missing)}")

    chunks = split_into_chunks(content)
    
    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": chunk}}]
            }
        }
        for chunk in chunks
    ]

    async with streamablehttp_client(
        url=MCP_SERVER_URL,
        headers={"Authorization": f"Bearer {MCP_AUTH_TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "API-post-page",
                {
                    "parent": {"page_id": PARENT_PAGE_ID},
                    "properties": {
                        "title": {
                            "title": [{"text": {"content": title}}]
                        }
                    },
                    "children": children
                }
            )
            return str(result)
