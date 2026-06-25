"""
project_manager.py — Ableton Live MCP Server
Gestión de proyectos musicales con persistencia en JSON.
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger("ableton-mcp")

PROJECTS_DIR = Path(__file__).parent.parent / "projects"
PROJECTS_DIR.mkdir(exist_ok=True)

_active_project: dict | None = None


def get_active_project() -> dict | None:
    return _active_project


def set_active_project(data: dict | None) -> None:
    global _active_project
    _active_project = data


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _project_path(slug: str) -> Path:
    return PROJECTS_DIR / slug


def _load_project_file(slug: str) -> dict | None:
    p = _project_path(slug) / "project.json"
    if p.exists():
        return json.loads(p.read_text())
    return None


def _save_project_file(data: dict) -> None:
    slug = data["slug"]
    path = _project_path(slug)
    path.mkdir(exist_ok=True)
    (path / "project.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info(f"Proyecto guardado: {slug}")
