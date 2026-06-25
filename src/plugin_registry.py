"""
plugin_registry.py — Ableton Live MCP Server
Registro persistente de plugins instalados en Ableton.
Permite cargar plugins por nombre en lugar de URI.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("ableton-mcp")

REGISTRY_DIR = Path(__file__).parent.parent / "registry"
REGISTRY_DIR.mkdir(exist_ok=True)

REGISTRY_FILE = REGISTRY_DIR / "plugins.json"

# Aliases de nombres comunes → nombre normalizado en el registry
PLUGIN_ALIASES: dict[str, list[str]] = {
    "maschine":      ["maschine 2", "maschine2", "ni maschine", "native instruments maschine"],
    "pigments":      ["arturia pigments", "pigments 4", "pigments4"],
    "reaktor":       ["reaktor 6", "reaktor6", "ni reaktor", "native instruments reaktor"],
    "audiolab":      ["audiolab v", "audiolabv", "arturia audiolab", "arturia audiolab v"],
    "audiofuse":     ["audiofuse studio", "arturia audiofuse"],
    "orbit":         ["orbit", "orbit by output", "output orbit"],
    # Efectos nativos comunes
    "reverb":        ["ableton reverb", "reverb"],
    "delay":         ["ableton delay", "delay"],
    "compressor":    ["compressor", "ableton compressor"],
    "eq8":           ["eq eight", "eq 8", "eight"],
    "saturator":     ["saturator"],
    "auto_filter":   ["auto filter", "autofilter"],
    "redux":         ["redux"],
    "corpus":        ["corpus"],
    "resonator":     ["resonator"],
    "vinyl":         ["vinyl distortion", "vinyl"],
}


def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("Registry corrupted, starting fresh")
    return {"plugins": {}, "favorites": {}, "last_scan": None}


def _save_registry(data: dict) -> None:
    REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"Registry guardado: {len(data.get('plugins', {}))} plugins")


def normalize_name(name: str) -> str:
    return name.lower().strip().replace(" ", "_").replace("-", "_")


def add_plugin_to_registry(name: str, uri: str, category: str = "", plugin_type: str = "") -> None:
    registry = _load_registry()
    key = normalize_name(name)
    registry["plugins"][key] = {
        "name": name,
        "uri": uri,
        "category": category,
        "type": plugin_type,
        "display_name": name,
    }
    _save_registry(registry)


def add_plugins_bulk(items: list[dict], category: str = "") -> int:
    """Agrega múltiples plugins al registry. Retorna cuántos se agregaron."""
    registry = _load_registry()
    added = 0
    for item in items:
        if not item.get("uri") or not item.get("name"):
            continue
        key = normalize_name(item["name"])
        plugin_type = item.get("type", category)
        registry["plugins"][key] = {
            "name": item["name"],
            "uri": item["uri"],
            "category": category,
            "type": plugin_type,
            "display_name": item["name"],
        }
        added += 1
    _save_registry(registry)
    return added


def find_plugin_uri(search_name: str) -> dict | None:
    """
    Busca un plugin por nombre. Intenta:
    1. Coincidencia exacta normalizada
    2. Búsqueda por alias
    3. Búsqueda por substring
    Retorna {name, uri, type} o None.
    """
    registry = _load_registry()
    plugins = registry.get("plugins", {})

    if not plugins:
        return None

    search = normalize_name(search_name)

    # 1. Exacto
    if search in plugins:
        return plugins[search]

    # 2. Alias
    for canonical, aliases in PLUGIN_ALIASES.items():
        if search in [normalize_name(a) for a in aliases] or search == canonical:
            if canonical in plugins:
                return plugins[canonical]
            # buscar variaciones del canonical
            for alias in aliases:
                key = normalize_name(alias)
                if key in plugins:
                    return plugins[key]

    # 3. Substring
    matches = [(k, v) for k, v in plugins.items() if search in k or search in normalize_name(v.get("name", ""))]
    if len(matches) == 1:
        return matches[0][1]
    if len(matches) > 1:
        # retornar el más corto (más específico)
        return sorted(matches, key=lambda x: len(x[0]))[0][1]

    return None


def search_plugins(query: str, limit: int = 20) -> list[dict]:
    """Busca plugins en el registry por nombre parcial."""
    registry = _load_registry()
    plugins = registry.get("plugins", {})
    q = normalize_name(query)
    results = [v for k, v in plugins.items() if q in k or q in normalize_name(v.get("name", ""))]
    return results[:limit]


def list_registry_summary() -> str:
    """Devuelve un resumen del registry para mostrar al usuario."""
    registry = _load_registry()
    plugins = registry.get("plugins", {})
    if not plugins:
        return "Registry vacío. Ejecuta build_plugin_registry con Ableton abierto."

    by_category: dict[str, list[str]] = {}
    for v in plugins.values():
        cat = v.get("category", "Other")
        by_category.setdefault(cat, []).append(v.get("display_name", v.get("name", "?")))

    lines = [f"📦 Registry: {len(plugins)} plugins"]
    for cat, names in sorted(by_category.items()):
        lines.append(f"\n  {cat} ({len(names)}):")
        for n in sorted(names)[:10]:
            lines.append(f"    • {n}")
        if len(names) > 10:
            lines.append(f"    ... y {len(names)-10} más")
    return "\n".join(lines)


def mark_as_scanned(timestamp: str) -> None:
    registry = _load_registry()
    registry["last_scan"] = timestamp
    _save_registry(registry)


def get_last_scan() -> str | None:
    return _load_registry().get("last_scan")
