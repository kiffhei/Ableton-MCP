# PROMPT_KICKOFF.md — Ableton Live MCP Server | Prompts de inicio para sesiones dedicadas
> Generado: 2026-06-17 · Auditoría en AUDIT.md · Plan en PLAN.md

---

## KICKOFF A — Sesión Claude Code (git + README + limpieza) `[45-60 min]`

```
Proyecto: Ableton Live MCP Server — Python MCP server que conecta Claude con Ableton Live.
Ruta local: ~/proyectos/ableton-mcp/
Objetivo de esta sesión: dejar el proyecto listo para publicar en GitHub.
Lee CLAUDE.md antes de tocar cualquier archivo.

TAREAS (en orden estricto — no cambiar el orden, el .gitignore va primero):

1. [DEV1] Crear .gitignore
   El .gitignore DEBE existir antes de git init. Ver DEV_TASKS.md DEV1 para contenido.
   Incluir projects/ para no commitear datos de producción personal.
   Incluir .claude/ para no commitear el settings.local.json.

2. [DEV4-B] Limpiar CLAUDE.md para repo público
   Opciones:
   - Opción A (recomendada): mover CLAUDE.md a CLAUDE.internal.md + agregar a .gitignore
     Crear CLAUDE.md público con solo: descripción técnica, herramientas, reglas de uso
   - Opción B: limpiar el CLAUDE.md existente quitando: "Sesión activa", "Librería de samples",
     "Referencia de hardware" — mantener solo info técnica del MCP
   PREGUNTAR a Brian qué opción prefiere antes de ejecutar.

3. [DEV3] Actualizar README con capacidades reales
   - Agregar elevator pitch al inicio
   - Tabla de 19 herramientas (en lugar de 7)
   - Sección de géneros: 60+, no solo 5
   - Aclarar que cualquier tonalidad/escala funciona
   - Agregar diagrama ASCII de arquitectura
   Ver DEV_TASKS.md DEV3 para contenido exacto.

4. [DEV2] Inicializar git y publicar en GitHub
   git init → verificar git status (projects/ NO debe aparecer) → primer commit → gh repo create
   Comando exacto en DEV_TASKS.md DEV2.

Verificación antes de push:
- git status: solo archivos que quieres en el repo
- python3 -m py_compile src/server.py (debe compilar sin errores)
- NO commitear projects/, .claude/, CLAUDE.internal.md
```

---

## KICKOFF B — Sesión Claude Code (refactor + tests) `[90-120 min]`

```
Proyecto: Ableton Live MCP Server. Ruta: ~/proyectos/ableton-mcp/
Asume que el repo ya está en GitHub (KICKOFF A completado).
Lee CLAUDE.md antes de cualquier cambio.

Esta sesión es refactor de arquitectura + tests básicos.
Las 19 tools deben seguir funcionando exactamente igual después del refactor.

1. [DEV5] Refactor server.py → módulos separados
   server.py tiene 1275 líneas. Separar en:
   - src/music_theory.py  (CHROMATIC, SCALES, CHORD_TYPES, GENRE_PATTERNS, build_chord, build_progression, helpers)
   - src/osc_client.py    (init_osc_client, send_osc, osc_response_handler, start_osc_listener)
   - src/project_manager.py (PROJECTS_DIR, _slug, _load_project_file, _save_project_file, _active_project)
   - src/server.py        (solo MCP server, list_tools, call_tool — importa de los otros módulos)
   Ver DEV_TASKS.md DEV5 para la separación exacta.
   
   VERIFICAR después: python3 -m py_compile src/server.py (y los otros módulos)

2. [DEV6] Tests de música theory
   Crear tests/test_music_theory.py con pytest.
   Agregar pytest a requirements.txt.
   Ver DEV_TASKS.md DEV6 para los tests mínimos a implementar.
   Comando: pytest tests/ -v
   
   Meta: al menos 10 tests verdes que no requieran Ableton instalado.

Commit por fase: primero refactor (sin tests), verificar que sigue compilando, luego tests.
```

---

## Nota sobre el orden de sesiones

**Hacer primero:** KICKOFF A (git + README). El proyecto no existe públicamente hasta hacer este paso.
**Después:** KICKOFF B (refactor) — una vez el repo existe y es visible.
**Simultáneo con KICKOFF A:** grabar el demo GIF (DESIGN_TASKS.md DT1) si Ableton está abierto.
