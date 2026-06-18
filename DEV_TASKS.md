# DEV_TASKS.md — Ableton Live MCP Server | Tareas de código
> Para sesión dedicada de Claude Code. Fecha: 2026-06-17.

---

## Contexto

MCP server en Python que conecta Claude con Ableton Live via AbletonOSC.
Ruta local: `~/proyectos/ableton-mcp/`
Stack: Python 3.10+ · mcp · python-osc
Archivo principal: `src/server.py` (1275 líneas, 19 tools)
Estado: funcional como herramienta, sin git, sin GitHub.

---

## DEV1 · Crear `.gitignore` `[XS]` — HACER PRIMERO

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyc
*.so
.env
venv/
.venv/
*.egg-info/

# Proyectos musicales (datos de producción personales)
projects/

# Claude Code interno
.claude/

# macOS
.DS_Store
*.DS_Store

# Editores
.vscode/
.idea/
```

**IMPORTANTE:** crear este archivo ANTES de `git init`.

---

## DEV2 · Inicializar git y publicar en GitHub `[S]`

```bash
cd ~/proyectos/ableton-mcp

# Verificar que .gitignore existe y projects/ no será commiteado
cat .gitignore | grep "projects"

# Inicializar
git init
git add .
git status  # verificar que projects/ NO aparece en staged

# Primer commit
git commit -m "feat: Ableton Live MCP server — 19 tools, music theory engine"

# Crear repo público en GitHub
gh repo create kiffhei/ableton-mcp --public --push --source=.
```

---

## DEV3 · Actualizar README — capacidades reales `[S]`

Archivo: `README.md`

**Cambios específicos:**

1. Agregar elevator pitch después del título:
   ```md
   > Controla Ableton Live con lenguaje natural via Claude Code.
   > Motor de teoría musical para progresiones en cualquier tonalidad/escala,
   > estado persistente de proyectos, y clonado de canciones reales vía Spotify.
   > Construido con el Model Context Protocol (MCP) de Anthropic.
   ```

2. Expandir tabla de herramientas (7 → 19):
   ```md
   | Herramienta | Descripción |
   |---|---|
   | `add_chord_progression` | Genera progresiones en cualquier tonalidad y escala |
   | `add_midi_notes` | Agrega notas MIDI individuales con control total |
   | `create_midi_track` | Crea un nuevo track MIDI con nombre y color |
   | `set_tempo` | Cambia el BPM del proyecto |
   | `play_pause` | Controla reproducción |
   | `get_session_info` | Info del proyecto: tracks, escenas, BPM |
   | `set_clip_color` | Colorea clips por índice RGB |
   | `load_instrument` | Carga un instrumento nativo de Ableton |
   | `load_plugin` | Carga un plugin VST/AU instalado |
   | `load_sample` | Carga un archivo WAV en un Simpler |
   | `get_device_params` | Lee los parámetros de un device/plugin |
   | `set_device_param` | Modifica un parámetro específico |
   | `set_device_params_bulk` | Modifica múltiples parámetros en una llamada |
   | `get_track_devices` | Lista los devices de un track |
   | `scan_plugins` | Escanea plugins instalados por nombre |
   | `new_project` | Crea un nuevo proyecto con estado persistente |
   | `load_project` | Carga el estado de un proyecto guardado |
   | `save_project_state` | Guarda el estado actual del proyecto |
   | `list_projects` | Lista todos los proyectos guardados |
   ```

3. Actualizar sección de estilos:
   ```md
   ### Géneros soportados

   60+ géneros con progresiones características predefinidas:
   house, deep_house, tech_house, afro_house, techno, minimal_techno,
   hip_hop, lo_fi, trap, drill, boom_bap, rnb, neo_soul, jazz, jazz_fusion,
   drum_and_bass, ambient, synthwave, afrobeats, amapiano, reggaeton, y más.

   Para cualquier estilo o combinación usa raíz + escala directamente:
   cualquier nota (C, F#, Bb...) × cualquier escala (mayor, menor, dórica,
   frigia, pentatónica, blues, doble armónica...).
   ```

4. Agregar sección "Arquitectura" con diagrama ASCII (ver DESIGN_TASKS.md DT2).

---

## DEV4 · Limpiar CLAUDE.md para repo público `[S]`

Decidir entre las dos opciones:

**Opción A (recomendada):** Mover CLAUDE.md actual a `CLAUDE.internal.md`:
```bash
mv CLAUDE.md CLAUDE.internal.md
echo "CLAUDE.internal.md" >> .gitignore
```
Crear `CLAUDE.md` público con solo la información técnica del MCP (sin rutas personales, sin sesión activa, sin equipamiento personal).

**Opción B:** Limpiar el CLAUDE.md existente:
- Remover toda la sección "Sesión activa"
- Remover "Librería de samples del usuario" (o reemplazar rutas con `[TU_RUTA_AQUI]`)
- Remover "Referencia de hardware equivalente" (equipamiento personal)
- Mantener: Flujo de inicio, MCPs disponibles, Sistema de tonalidades, Flujo de clonado, Reglas de comportamiento, Referencia de instrumentos, Efectos por género, Géneros disponibles

---

## DEV5 · Refactor: separar server.py en módulos `[L]`

`server.py` tiene 1275 líneas. Separar en:

```
src/
├── server.py          (~200 líneas: MCP server, list_tools, call_tool)
├── music_theory.py    (~300 líneas: CHROMATIC, SCALES, CHORD_TYPES, GENRE_PATTERNS, helpers)
├── osc_client.py      (~80 líneas: init_osc_client, send_osc, osc_response_handler, start_osc_listener)
└── project_manager.py (~100 líneas: PROJECTS_DIR, _slug, _load_project_file, _save_project_file)
```

Imports en server.py:
```python
from music_theory import build_chord, build_progression, note_name_to_midi, scale_degree_to_root
from osc_client import init_osc_client, send_osc, start_osc_listener
from project_manager import new_project, load_project, save_project
```

**Beneficio para portafolio:** cualquier reclutador que abra el repo ve módulos cohesivos, no un monolito.

---

## DEV6 · Agregar tests de música theory `[M]`

Requiere DEV5 (separar music_theory.py para poder importarlo sin el servidor MCP).

Crear `tests/test_music_theory.py`:
```python
import pytest
import sys
sys.path.insert(0, "src")
from music_theory import note_name_to_midi, scale_degree_to_root, build_chord, build_progression

def test_note_to_midi_c4():
    assert note_name_to_midi("C", 4) == 60

def test_note_to_midi_a4():
    assert note_name_to_midi("A", 4) == 69

def test_scale_c_major():
    from music_theory import SCALES, NOTE_TO_MIDI
    root = NOTE_TO_MIDI["C"]
    scale = [root + i for i in SCALES["major"]]
    assert scale == [60, 62, 64, 65, 67, 69, 71]

def test_build_chord_major():
    notes = build_chord(60, "maj")  # C mayor
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 64, 67]  # C E G

def test_build_chord_minor():
    notes = build_chord(60, "min")  # C menor
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 63, 67]  # C Eb G
```

Instalar pytest: agregar `pytest>=8.0` a `requirements.txt`.
Comando: `pytest tests/ -v`

---

## Orden de ejecución

1. **DEV1** → 5 min
2. **DEV4** → 15 min (limpiar CLAUDE.md antes del primer commit)
3. **DEV3** → 30 min (actualizar README)
4. **DEV2** → 10 min (git init + GitHub)
5. **DEV5** → 60 min (refactor en módulos — sesión separada)
6. **DEV6** → 30 min (tests — requiere DEV5)
