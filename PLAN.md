# PLAN.md — Ableton Live MCP Server | Plan de acción post-auditoría
> Criterio: portafolio público visible. Fecha: 2026-06-17.

---

## CRÍTICO — Bloquea mostrar el proyecto

### C1 · Inicializar git y publicar en GitHub `[S]`
**Problema:** sin repo, el proyecto no existe para reclutadores.
**Pasos:**
```bash
cd ~/proyectos/ableton-mcp

# Crear .gitignore PRIMERO (antes de git init)
# (ver C2 — hacerlo antes)

git init
git add .
git commit -m "feat: Ableton Live MCP server — 19 tools, music theory engine, project persistence"

# Crear repo en GitHub
gh repo create kiffhei/ableton-mcp --public --push --source=.
```
Asegurarse de que `projects/` y datos personales estén en `.gitignore` antes del primer commit.

---

### C2 · Crear `.gitignore` antes del primer commit `[XS]`
```
# Python
__pycache__/
*.py[cod]
*.so
.env
venv/
.venv/

# Proyectos musicales (datos de producción personales)
projects/

# Claude Code interno
.claude/

# macOS
.DS_Store
```
**CRÍTICO:** `projects/` contiene `digital-simbiosis/project.json` con el estado de la producción real. No debe estar en el repo público.

---

### C3 · Actualizar README con capacidades reales `[S]`
**Problema:** README muestra 37% de las capacidades. Subestima el proyecto masivamente.

**Cambios:**
1. Actualizar tabla de herramientas: 7 → 19 tools (agregar set_clip_color, load_instrument, get_device_params, set_device_param, set_device_params_bulk, get_track_devices, scan_plugins, load_plugin, load_sample, new_project, load_project, save_project_state, list_projects)
2. Actualizar sección de estilos: 5 → 60+ géneros. Cambiar el listado a un párrafo: "Soporta 60+ géneros con progresiones características predefinidas (house, techno, hip-hop, jazz, afrobeats, reggaeton...) y modo libre para cualquier combinación de raíz y escala."
3. Actualizar "Tonalidades" — aclarar que funciona con CUALQUIER nota/escala, no solo Am, Dm, etc.
4. Agregar sección "Capacidades avanzadas": clonado de canciones reales vía Spotify, persistencia de proyectos, gestión de parámetros de efectos en bulk

---

### C4 · Limpiar CLAUDE.md para repo público `[S]`
**Problema:** contiene ruta personal `/Volumes/KiffHei/...`, lista de equipamiento personal, y contexto de producción actual.

**Opciones:**
- **A (recomendada):** mover CLAUDE.md actual a `CLAUDE.internal.md` en `.gitignore`. Crear `CLAUDE.md` público con solo: descripción, herramientas, reglas de uso del MCP.
- **B:** reemplazar `/Volumes/KiffHei/...` con `[TU_RUTA_DE_SAMPLES]` y remover la sección "Sesión activa" antes de commitear.

---

## IMPORTANTE — Mejora sustancial de percepción

### I1 · Agregar elevator pitch al inicio del README `[XS]`
El README actual empieza con el título y los requisitos. Falta el hook que le dice al reclutador POR QUÉ importa.

Agregar después del título:
```md
> Controla Ableton Live con lenguaje natural. Crea progresiones en cualquier 
> tonalidad y escala, maneja el estado de proyectos de producción, y puede 
> analizar y clonar la estructura musical de canciones reales vía Spotify.
> Construido con el Model Context Protocol (MCP) de Anthropic.
```

### I2 · Agregar demo en README `[M]`
Un GIF de 30 segundos mostrando Claude controlando Ableton en tiempo real es el diferenciador máximo de este proyecto. Nadie ha visto esto.

**Contenido sugerido:**
1. Claude recibe: "Crea un bassline de deep house en Dm"
2. Claude llama `create_midi_track`, `add_chord_progression`
3. Ableton muestra el clip creado en tiempo real
4. Reproducción del clip

Herramienta: QuickTime Player → Grab → Screen Recording + export GIF con ffmpeg o Gifox.

### I3 · Separar server.py en módulos `[L]`
1275 líneas en un solo archivo. Para portafolio no es bloqueante, pero para credibilidad técnica sería mejor:
- `src/music_theory.py` — CHROMATIC, NOTE_TO_MIDI, SCALES, CHORD_TYPES, GENRE_PATTERNS, build_chord, build_progression
- `src/osc_client.py` — init_osc_client, send_osc, start_osc_listener
- `src/project_manager.py` — PROJECTS_DIR, _slug, _load_project_file, _save_project_file
- `src/server.py` — solo el MCP server, list_tools, call_tool

### I4 · Agregar tests de música theory `[M]`
La lógica matemática de `note_name_to_midi`, `scale_degree_to_root`, `build_chord` es pura y testeable sin Ableton.

Crear `tests/test_music_theory.py`:
```python
# pytest — sin necesidad de Ableton instalado
def test_note_to_midi():
    assert note_name_to_midi("C", 4) == 60
    assert note_name_to_midi("A", 4) == 69

def test_scale_major():
    # C major: C D E F G A B
    # Primero necesitamos refactorizar para importar desde music_theory.py
    pass
```
Requiere el refactor I3 para poder importar las funciones sin inicializar el servidor MCP.

---

## NICE-TO-HAVE

### N1 · GitHub Actions básico `[S]`
```yaml
# Solo para lint y syntax check — no requiere Ableton
- run: pip install flake8
- run: flake8 src/ --max-line-length=120
- run: python -m py_compile src/server.py
```

### N2 · Tabla de todos los géneros en README `[XS]`
Los 60+ géneros ya están en CLAUDE.md. Copiar la lista de `## Géneros disponibles` al README.

### N3 · Agregar descripción de la arquitectura en README `[S]`
Un diagrama ASCII mostrando el flujo:
```
Claude Code ──MCP protocol──► server.py ──OSC port 11000──► AbletonOSC ──► Ableton Live
                                   ▲
                             projects/*.json (estado persistente)
```

---

## Orden de ejecución recomendado

1. **C2** → 5 min, crear .gitignore primero
2. **C4-A** → 10 min, mover CLAUDE.md a .gitignore antes del primer commit
3. **I1** → 5 min, agregar elevator pitch al README
4. **C3** → 30 min, actualizar README con capacidades reales
5. **C1** → 10 min, `git init && gh repo create`
6. **I2** → 60 min, grabar GIF demo (tiene el mayor impacto de portafolio)
7. **I3 + I4** → sesiones separadas de refactor y tests
