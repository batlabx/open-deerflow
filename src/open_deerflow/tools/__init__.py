"""MCP tool servers.

Each file in this package is a standalone MCP server (FastMCP) exposing one
capability over stdio. They are launched as subprocesses by the graph via
``langchain-mcp-adapters`` and can equally be used by Claude Desktop, Cursor,
or any other MCP client — that portability is the whole point of putting
capabilities behind MCP instead of hard-coding them.
"""
