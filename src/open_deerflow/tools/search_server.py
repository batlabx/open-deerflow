"""MCP server: web_search.

Why is search a TOOL and not a skill?
  It is a deterministic capability with a side effect (a network call) and a
  typed contract: query -> [{title, url, snippet}]. The model should *invoke*
  it, not reason about how to perform it. Anything with an API boundary and a
  verifiable return value belongs behind MCP.

Open-source swap: DeerFlow defaults to the paid Tavily/Brave APIs. We default
to a self-hosted SearxNG instance and fall back to the keyless DuckDuckGo
backend so the server works with zero configuration.
"""
from __future__ import annotations

import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("open-deerflow-search")

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")


@mcp.tool()
def web_search(query: str, max_results: int = 6) -> list[dict]:
    """Search the web. Returns a list of {title, url, snippet}."""
    # 1) Preferred: a self-hosted SearxNG instance (private, unlimited, free).
    try:
        resp = httpx.get(
            f"{SEARXNG_URL}/search",
            params={"q": query, "format": "json"},
            timeout=15,
        )
        resp.raise_for_status()
        hits = resp.json().get("results", [])[:max_results]
        if hits:
            return [
                {"title": h.get("title"), "url": h.get("url"),
                 "snippet": h.get("content", "")}
                for h in hits
            ]
    except Exception:
        pass  # SearxNG not running -> fall through to the keyless backend

    # 2) Fallback: DuckDuckGo via the `ddgs` package (no API key required).
    from ddgs import DDGS

    with DDGS() as ddg:
        return [
            {"title": h["title"], "url": h["href"], "snippet": h["body"]}
            for h in ddg.text(query, max_results=max_results)
        ]


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
