"""
rhythm_tools.py — Ableton Live MCP Server
Handler MCP para los patrones rítmicos medidos que viven en knowledge/.
"""

import json
from pathlib import Path

from mcp import types

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
GENRE_FILES = {
    "melodic techno": "kick_bass_melodic_techno.json",
}
_cache: dict[str, dict] = {}


def normalize_genre(raw: str) -> str:
    return " ".join(str(raw).lower().replace("_", " ").replace("-", " ").split())


def load_knowledge(genre: str) -> dict:
    """Lee y cachea el JSON de un género. Lanza si falta o está corrupto."""
    filename = GENRE_FILES[genre]
    if filename in _cache:
        return _cache[filename]
    path = KNOWLEDGE_DIR / filename
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Falta {path}. El género '{genre}' está registrado pero su archivo no existe."
        )
    except json.JSONDecodeError as error:
        raise ValueError(f"{path} no es JSON válido: {error}") from error
    _cache[filename] = data
    return data


def format_loop(loop: dict) -> str:
    voces = " + ".join(
        f"{v['nota']} en pasos {v['pasos']}" for v in loop["voces"]
    )
    etiqueta = loop["etiqueta_del_anuncio"]
    aviso = "" if loop["coincide"] else f"  (el anuncio la rotula '{etiqueta}')"
    return f"  {loop['nombre']:<10} raíz {loop['raiz_medida']}{aviso}\n    {voces}"


def get_rhythm_pattern(arguments: dict) -> list[types.TextContent]:
    genre = normalize_genre(arguments.get("genre", ""))
    bpm = arguments.get("bpm")

    if genre not in GENRE_FILES:
        disponibles = ", ".join(sorted(GENRE_FILES))
        return [types.TextContent(
            type="text",
            text=(
                f"❌ No hay patrones medidos para '{arguments.get('genre')}'.\n"
                f"Géneros disponibles: {disponibles}\n"
                "Estos patrones salen de mediciones, no de plantillas: solo existen "
                "los géneros que se han analizado."
            ),
        )]

    try:
        data = load_knowledge(genre)
    except (FileNotFoundError, ValueError) as error:
        return [types.TextContent(type="text", text=f"❌ {error}")]

    nativo = data["tempo_bpm"]
    aviso_tempo = ""
    if bpm is not None and int(bpm) != nativo:
        aviso_tempo = (
            f"\n⚠️  Medido a {nativo} BPM; lo pediste a {bpm}. Los pasos son "
            "relativos al compás, así que el patrón se traslada, pero el carácter "
            "cambia: a más BPM el bajo rodante se vuelve más agresivo.\n"
        )

    lineas = [
        f"🎛️  {genre} — {len(data['loops'])} loops medidos a {nativo} BPM",
        f"\n{data['grid']}",
        f"\nKick: pasos {data['kick']['cierto']} (4 en el piso).",
        f"  {data['kick']['nota']}",
        f"\nDuración: {data['duracion_de_nota']}",
        aviso_tempo,
        "\nBajos:",
    ]
    lineas += [format_loop(loop) for loop in data["loops"]]
    lineas.append(f"\nTonalidades: {data['sobre_las_etiquetas_de_tonalidad']}")
    lineas.append(f"\nFuente: {data['fuente']}")

    return [types.TextContent(type="text", text="\n".join(lineas))]


HANDLERS = {
    "get_rhythm_pattern": get_rhythm_pattern,
}
