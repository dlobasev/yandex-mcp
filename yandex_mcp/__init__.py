"""Yandex MCP Server - MCP server for Yandex Direct and Yandex Metrika APIs."""

# Import tools to register them with the MCP server
import yandex_mcp.tools  # noqa: F401
from yandex_mcp.server import mcp  # noqa: F401

__all__ = ["mcp"]
