import asyncio
import os

from langchain_core.tools import tool

from notion_mcp.notion_mcp_client import create_page


NOTION_ENV_KEYS = ("MCP_SERVER_URL", "MCP_AUTH_TOKEN", "PARENT_PAGE_ID")


def is_notion_configured() -> bool:
    """Return whether every setting required by the Notion MCP tool exists."""

    return all(os.getenv(key) for key in NOTION_ENV_KEYS)


@tool
def save_notes_to_notion(title: str, content: str) -> str:
    """
    Save study notes or exam material to Notion.
    Use this when the user asks to save, write, or store notes in Notion.
    """
    if not is_notion_configured():
        missing = ", ".join(key for key in NOTION_ENV_KEYS if not os.getenv(key))
        return f"Notion integration is not configured. Missing: {missing}."
    return asyncio.run(create_page(title, content))
