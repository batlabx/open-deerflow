"""MCP server: read_url (crawl + extract).

Turns a messy web page into clean, LLM-ready text. DeerFlow uses a hosted
reader (Jina); we use `trafilatura`, the best open-source boilerplate remover,
so no data leaves the machine and there is nothing to pay for.

Still a TOOL, for the same reason as search: an API boundary (url -> text) with
a network side effect.
"""
from __future__ import annotations

import httpx
import trafilatura
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("open-deerflow-crawl")


@mcp.tool()
def read_url(url: str, max_chars: int = 8000) -> dict:
    """Fetch a URL and return {url, title, text} with navigation/ads stripped."""
    html = httpx.get(
        url,
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "open-deerflow/0.1 (+https://github.com)"},
    ).text

    text = trafilatura.extract(html, include_links=False, favor_recall=True) or ""
    meta = trafilatura.extract_metadata(html)
    title = getattr(meta, "title", "") if meta else ""

    return {"url": url, "title": title, "text": text[:max_chars]}


if __name__ == "__main__":
    mcp.run()
