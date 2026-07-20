"""
project_tools.py — Ableton Live MCP Server
Handlers MCP para gestión de proyectos (new/load/save/list).
Wrappers finos sobre la persistencia de project_manager.py.
"""

import time
from datetime import date

from mcp import types

from osc_client import send_osc, osc_lock, osc_responses
from project_manager import (
    PROJECTS_DIR, _slug, _project_path,
    _load_project_file, _save_project_file,
    get_active_project, set_active_project,
)


def new_project(arguments: dict) -> list[types.TextContent]:
    proj_name  = arguments["name"]
    slug       = _slug(proj_name)
    bpm        = arguments["bpm"]
    root_note  = arguments.get("root_note", "C")
    mode       = arguments.get("mode", "minor")
    genre      = arguments.get("genre", "")
    reference  = arguments.get("reference", "")
    notes      = arguments.get("notes", "")

    existing = _load_project_file(slug)
    if existing:
        set_active_project(existing)
        return [types.TextContent(type="text", text=(
            f"⚠️ Proyecto '{proj_name}' ya existe (slug: {slug}).\n"
            f"Cargado como proyecto activo. Usa load_project para retomarlo "
            f"o elige otro nombre para crear uno nuevo."
        ))]

    data = {
        "name": proj_name,
        "slug": slug,
        "created": str(date.today()),
        "last_updated": str(date.today()),
        "production": {
            "genre": genre,
            "bpm": bpm,
            "root_note": root_note,
            "mode": mode,
            "reference": reference,
        },
        "tracks": [],
        "arrangement": {},
        "mixing": {"status": "pending", "todo": []},
        "notes": notes,
    }
    _save_project_file(data)
    set_active_project(data)

    send_osc("/live/song/set/tempo", float(bpm))

    proj_dir = _project_path(slug)
    (proj_dir / "session.md").write_text(
        f"# {proj_name}\n\n"
        f"**Género:** {genre}  \n"
        f"**BPM:** {bpm}  \n"
        f"**Tonalidad:** {root_note} {mode}  \n"
        f"**Referencia:** {reference}  \n\n"
        f"## Sesión {date.today()}\n\n{notes}\n"
    )

    return [types.TextContent(type="text", text=(
        f"✅ Proyecto '{proj_name}' creado\n"
        f"📁 Carpeta: ableton-mcp/projects/{slug}/\n"
        f"🎵 BPM seteado a {bpm}\n"
        f"🎼 Tonalidad: {root_note} {mode}\n\n"
        f"Archivos creados:\n"
        f"  • project.json — contexto completo\n"
        f"  • session.md   — notas de sesión\n\n"
        f"Próximo paso: crea los tracks con create_midi_track y "
        f"carga los instrumentos con load_instrument."
    ))]


def load_project(arguments: dict) -> list[types.TextContent]:
    proj_name = arguments["name"]
    slug = _slug(proj_name)
    data = _load_project_file(slug)
    if data is None:
        projects = [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]
        return [types.TextContent(type="text", text=(
            f"❌ Proyecto '{proj_name}' no encontrado (slug: {slug}).\n"
            f"Proyectos disponibles: {', '.join(projects) or 'ninguno'}"
        ))]
    set_active_project(data)
    prod = data.get("production", {})
    tracks = data.get("tracks", [])
    track_lines = "\n".join(
        f"  [{t['index']}] {t['name']} — {t.get('instrument','?')} ({t.get('status','?')})"
        for t in tracks
    ) or "  (sin tracks guardados)"
    return [types.TextContent(type="text", text=(
        f"✅ Proyecto '{data['name']}' cargado\n"
        f"🎵 BPM: {prod.get('bpm','?')} | Tonalidad: {prod.get('root_note','?')} {prod.get('mode','?')}\n"
        f"🎸 Género: {prod.get('genre','?')}\n"
        f"📀 Referencia: {prod.get('reference','')}\n\n"
        f"Tracks guardados:\n{track_lines}\n\n"
        f"📅 Última actualización: {data.get('last_updated','?')}"
    ))]


def save_project_state(arguments: dict) -> list[types.TextContent]:
    active = get_active_project()
    if active is None:
        return [types.TextContent(type="text", text=(
            "❌ No hay proyecto activo. Usa new_project o load_project primero."
        ))]
    session_notes = arguments.get("notes", "")
    active["last_updated"] = str(date.today())

    send_osc("/live/song/get/tempo")
    time.sleep(0.4)
    with osc_lock:
        tempo = osc_responses.get("/live/song/get/tempo", (None,))[0]
    if tempo:
        active["production"]["bpm"] = tempo

    _save_project_file(active)

    slug = active["slug"]
    session_file = _project_path(slug) / "session.md"
    if session_notes and session_file.exists():
        existing = session_file.read_text()
        session_file.write_text(
            existing + f"\n### Update {date.today()}\n{session_notes}\n"
        )

    return [types.TextContent(type="text", text=(
        f"✅ Proyecto '{active['name']}' guardado\n"
        f"📁 ableton-mcp/projects/{slug}/project.json actualizado"
    ))]


def list_projects(arguments: dict) -> list[types.TextContent]:
    projects = []
    for p in sorted(PROJECTS_DIR.iterdir()):
        if p.is_dir():
            data = _load_project_file(p.name)
            if data:
                prod = data.get("production", {})
                projects.append(
                    f"  📁 {data['name']} ({p.name})\n"
                    f"     {prod.get('genre','')} | {prod.get('bpm','')} BPM | "
                    f"{prod.get('root_note','')} {prod.get('mode','')} | "
                    f"Updated: {data.get('last_updated','?')}"
                )
    if not projects:
        return [types.TextContent(type="text", text="No hay proyectos guardados. Usa new_project para crear uno.")]
    return [types.TextContent(type="text", text="🎵 Proyectos en ableton-mcp:\n\n" + "\n\n".join(projects))]


HANDLERS = {
    "new_project": new_project,
    "load_project": load_project,
    "save_project_state": save_project_state,
    "list_projects": list_projects,
}
