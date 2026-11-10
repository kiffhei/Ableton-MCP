"""
free_tools.py — Ableton Live MCP Server
Base de conocimiento de herramientas gratuitas de terceros (Max for Live devices,
Live Extensions, plugins) que el MCP puede recomendar antes de construir un
recurso musical desde cero vía OSC.
"""

import json
import re
import unicodedata
from pathlib import Path

KB_FILE = Path(__file__).parent.parent / "tools_knowledge_base.json"

_STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en",
    "y", "o", "a", "para", "por", "con", "sin", "que", "es", "al", "the",
    "an", "of", "for", "with", "to", "and", "or", "sobre", "como", "cada",
    "todo", "toda", "todos", "todas", "esta", "este", "ese", "esa",
    "via", "usar", "usando", "hacer",
}

_MIN_OVERLAP = 2


def _load_kb() -> list[dict]:
    if not KB_FILE.exists():
        return []
    try:
        return json.loads(KB_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _normalize(text: str) -> set[str]:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    words = re.findall(r"[a-z0-9]+", text)
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def _tool_vocabulary(tool: dict) -> set[str]:
    vocab: set[str] = set()
    vocab |= _normalize(tool.get("name", ""))
    vocab |= _normalize(tool.get("description", ""))
    for use_case in tool.get("use_cases", []):
        vocab |= _normalize(use_case)
    return vocab


def is_installed(tool: dict) -> bool:
    install_path = tool.get("install_path", "")
    if not install_path:
        return False
    path = Path(__file__).parent.parent / install_path
    return path.exists()


def suggest_tool(task_description: str, limit: int = 3) -> list[dict]:
    """
    Match semántico simple por solapamiento de palabras entre task_description
    y (name + description + use_cases) de cada tool. Sin dependencias externas
    de NLP — suficiente para distinguir "separar batería en stems" de
    "generar un patrón rítmico".
    """
    task_words = _normalize(task_description)
    if not task_words:
        return []

    scored: list[tuple[int, dict]] = []
    for tool in _load_kb():
        overlap = len(task_words & _tool_vocabulary(tool))
        if overlap >= _MIN_OVERLAP:
            scored.append((overlap, tool))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [tool for _, tool in scored[:limit]]


def format_suggestion(tool: dict) -> str:
    installed = is_installed(tool)
    status = "✅ ya está descargado localmente" if installed else "⬇️ no está descargado todavía"

    lines = [
        f"🎛️ {tool['name']} ({tool.get('resource_type', tool.get('category', ''))})",
        f"{status}",
        "",
        tool.get("description", ""),
        "",
        f"Requiere: {tool.get('requires', '?')}",
        f"Licencia: {tool.get('license', '?')}",
    ]

    if not installed and tool.get("requires_manual_download"):
        lines.append("⚠️ La descarga no es automatizable (bloqueada por protección anti-bot del sitio) — debe bajarse manualmente desde el navegador.")

    if tool.get("requires_manual_install"):
        lines.append("⚠️ Requiere instalación manual del usuario (instalador) — el MCP no lo instala automáticamente.")

    if not installed:
        lines.append(f"Fuente: {tool.get('source_url', '?')}")
    else:
        lines.append(f"Ubicación local: {tool.get('install_path', '?')}")

    lines.append(f"Instalación: {tool.get('install_instructions', '?')}")

    return "\n".join(lines)
