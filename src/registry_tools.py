"""
registry_tools.py — Ableton Live MCP Server
Handlers MCP para el registry de plugins: construcción, carga por nombre y búsqueda.
"""

import time
from datetime import datetime

from mcp import types

from osc_client import send_osc, osc_lock, osc_responses
from plugin_registry import (
    add_plugins_bulk, find_plugin_uri, search_plugins,
    list_registry_summary, mark_as_scanned, get_last_scan,
    _parse_browser_items,
)


def build_plugin_registry(arguments: dict) -> list[types.TextContent]:
    force = arguments.get("force_rescan", False)
    last = get_last_scan()
    if last and not force:
        summary = list_registry_summary()
        return [types.TextContent(
            type="text",
            text=(
                f"📦 Registry ya existe (último scan: {last})\n\n"
                f"{summary}\n\n"
                "Usa force_rescan=true para re-escanear."
            ),
        )]

    categories_arg = arguments.get("categories", [])
    search_terms = categories_arg if categories_arg else ["", "VST", "AU", "Max"]

    total_added = 0
    scan_log: list[str] = []

    for term in search_terms:
        send_osc("/live/browser/scan", term)
        time.sleep(2.0)

        with osc_lock:
            raw = osc_responses.get("/live/browser/scan", ())

        items = _parse_browser_items(raw)
        loadable = [it for it in items if it.get("loadable") and it.get("uri")]

        category = term or "General"
        added = add_plugins_bulk(loadable, category=category)
        total_added += added
        scan_log.append(f"  '{term}' → {len(items)} items, {added} plugins")

    mark_as_scanned(datetime.now().isoformat())
    summary = list_registry_summary()

    return [types.TextContent(
        type="text",
        text=(
            f"✅ Plugin Registry construido\n\n"
            f"Escaneos realizados:\n" + "\n".join(scan_log) + "\n\n"
            f"{summary}\n\n"
            "💡 Ahora puedes usar load_plugin_by_name con nombres como:\n"
            "   'Maschine 2', 'Arturia Pigments', 'Reaktor 6', 'Orbit'"
        ),
    )]


def load_plugin_by_name(arguments: dict) -> list[types.TextContent]:
    track_idx   = arguments["track_index"]
    plugin_name = arguments["plugin_name"].strip()

    result = find_plugin_uri(plugin_name)

    if result is None:
        matches = search_plugins(plugin_name)
        if matches:
            options = "\n".join(f"  • {m['display_name']} ({m.get('type','')})" for m in matches[:10])
            return [types.TextContent(
                type="text",
                text=(
                    f"⚠️ '{plugin_name}' no encontrado exactamente. ¿Quisiste decir:\n{options}\n\n"
                    "Intenta con el nombre exacto, o usa scan_plugins para ver URIs directas."
                ),
            )]
        return [types.TextContent(
            type="text",
            text=(
                f"❌ '{plugin_name}' no encontrado en el registry.\n\n"
                "Ejecuta build_plugin_registry con Ableton abierto para actualizar la lista.\n"
                "Luego usa search_plugin_registry para buscar nombres disponibles."
            ),
        )]

    plugin_uri = result["uri"]
    display    = result.get("display_name", plugin_name)

    send_osc("/live/view/set/selected_track", track_idx)
    time.sleep(0.3)
    send_osc("/live/track/load_device", track_idx, plugin_uri)
    time.sleep(1.5)

    return [types.TextContent(
        type="text",
        text=(
            f"✅ {display} cargado en Track {track_idx + 1}\n"
            f"📍 URI: {plugin_uri}\n"
            f"🏷️ Tipo: {result.get('type','')}\n"
            "💡 Usa get_track_devices para confirmar la carga.\n"
            "💡 Usa get_device_params para explorar sus parámetros."
        ),
    )]


def search_plugin_registry(arguments: dict) -> list[types.TextContent]:
    query = arguments["query"]
    limit = arguments.get("limit", 20)
    results = search_plugins(query, limit)

    if not results:
        summary = list_registry_summary()
        return [types.TextContent(
            type="text",
            text=(
                f"🔍 Sin resultados para '{query}'\n\n"
                f"Estado del registry:\n{summary}"
            ),
        )]

    lines = [f"🔍 Plugins que coinciden con '{query}':"]
    for r in results:
        lines.append(f"  • {r['display_name']}  ({r.get('type','')})")
        if r.get("uri"):
            uri_short = r["uri"][:60] + "…" if len(r["uri"]) > 60 else r["uri"]
            lines.append(f"    URI: {uri_short}")
    lines.append(f"\n💡 Usa load_plugin_by_name(track_index=N, plugin_name='<nombre>') para cargar.")
    return [types.TextContent(type="text", text="\n".join(lines))]


HANDLERS = {
    "build_plugin_registry": build_plugin_registry,
    "load_plugin_by_name": load_plugin_by_name,
    "search_plugin_registry": search_plugin_registry,
}
