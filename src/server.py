"""
Ableton Live MCP Server
Conecta Claude con Ableton Live via AbletonOSC
"""

import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from osc_client import init_osc_client, start_osc_listener
from tool_definitions import TOOL_DEFINITIONS
from transport_tools import HANDLERS as TRANSPORT_HANDLERS
from clip_tools import HANDLERS as CLIP_HANDLERS
from device_tools import HANDLERS as DEVICE_HANDLERS
from track_tools import HANDLERS as TRACK_HANDLERS
from project_tools import HANDLERS as PROJECT_HANDLERS
from registry_tools import HANDLERS as REGISTRY_HANDLERS
from free_tools_handlers import HANDLERS as FREE_TOOLS_HANDLERS
from rhythm_tools import HANDLERS as RHYTHM_HANDLERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ableton-mcp")

# ── Servidor MCP ────────────────────────────────────────────
app = Server("ableton-mcp")

# ── Dispatch de tools por nombre → handler ──────────────────
HANDLERS = {
    **TRANSPORT_HANDLERS,
    **CLIP_HANDLERS,
    **DEVICE_HANDLERS,
    **TRACK_HANDLERS,
    **PROJECT_HANDLERS,
    **REGISTRY_HANDLERS,
    **FREE_TOOLS_HANDLERS,
    **RHYTHM_HANDLERS,
}


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOL_DEFINITIONS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    handler = HANDLERS.get(name)
    if handler is None:
        return [types.TextContent(type="text", text=f"❌ Herramienta '{name}' no reconocida")]
    return handler(arguments)


# ── Entry point ──────────────────────────────────────────────

async def main():
    init_osc_client()
    start_osc_listener()
    logger.info("🎛️ Ableton MCP Server iniciado — esperando conexiones...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
