"""
free_tools_handlers.py — Ableton Live MCP Server
Handler MCP para recomendar herramientas gratuitas de terceros antes de
construir un recurso musical desde cero vía OSC.
"""

from mcp import types

from free_tools import suggest_tool, format_suggestion


def suggest_free_tool(arguments: dict) -> list[types.TextContent]:
    task_description = arguments["task_description"]
    matches = suggest_tool(task_description)

    if not matches:
        return [types.TextContent(
            type="text",
            text=(
                f"🔍 Ninguna herramienta gratuita en la base de conocimiento cubre "
                f"'{task_description}'.\n\n"
                "Procede a construirlo desde cero vía OSC (add_chord_progression, "
                "add_midi_notes, generate_chord_progression, etc.)."
            ),
        )]

    lines = ["Antes de construir esto desde cero vía OSC, considera:\n"]
    for tool in matches:
        lines.append(format_suggestion(tool))
        lines.append("")

    return [types.TextContent(type="text", text="\n".join(lines).strip())]


HANDLERS = {
    "suggest_free_tool": suggest_free_tool,
}
