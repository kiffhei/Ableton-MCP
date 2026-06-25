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

## KICKOFF C — Sesión Claude Code (bridge Node for Max ↔ Claude Code) `[60-90 min]`

```
Proyecto: Ableton Live MCP Server — extensión "M4L Channel Strip".
Ruta local: ~/proyectos/ableton-mcp/
Objetivo de esta sesión: crear el bridge en Node for Max que permite invocar Claude Code
(con el MCP server "ableton" ya configurado) desde un device de Max for Live colocado
en un canal de Ableton, sin tocar server.py.

Lee CLAUDE.md y AUDIT.md antes de tocar cualquier archivo.
AUDIT.md ya documenta que load_instrument/load_plugin/scan_plugins/load_sample llaman
a endpoints OSC inexistentes en AbletonOSC estándar — NO es parte de esta sesión
arreglarlo. Si una prueba E2E falla específicamente en una de esas 4 tools, es un
problema conocido y separado, no un bug del bridge.

TAREAS (en orden estricto — DEV8 bloquea todo lo demás, va primero):

1. [DEV8] Verificar que el MCP server "ableton" responde en modo headless
   Correr los dos comandos exactos de DEV_TASKS.md DEV8.
   Si `claude mcp list` no muestra "ableton" conectado, DETENTE y reporta el error
   tal cual — no continuar con el resto de la sesión sin esto resuelto.

2. [DEV9] Resolver la ruta absoluta del binario claude
   `which claude` → guardar el valor, se usa en el siguiente paso.

3. [DEV7] Crear m4l-bridge/ con bridge-simple.js, bridge-persistent.js y package.json
   Ver DEV_TASKS.md DEV7 para el contenido exacto.
   Reemplazar CLAUDE_BIN_PLACEHOLDER con la ruta de DEV9 en ambos archivos.
   Reemplazar TU_USUARIO con el usuario real (`whoami`) en REPO_PATH.

4. [DEV10] Test E2E del bridge simple, sin Max
   Crear m4l-bridge/test-bridge.js (ver DEV_TASKS.md DEV10).
   PREGUNTAR a Brian si Ableton Live está abierto con AbletonOSC activo antes de correrlo.
   Correr: node m4l-bridge/test-bridge.js
   Verificación: el track 0 muestra el clip generado, JSON de salida con is_error: false.

5. [DEV11] Migrar a bridge-persistent.js — SOLO si el paso 4 pasó sin errores
   Si DEV10 falló, quedarse ahí y depurar; no avanzar a este paso.

NO HACER en esta sesión:
- NO tocar server.py — el bridge no lo necesita, habla con él vía Claude Code/stdio.
- NO intentar crear o editar el archivo .amxd del patch de Max — eso es DT4 en
  DESIGN_TASKS.md, una tarea manual de Brian en la GUI de Max, fuera de tu alcance.
- NO usar --dangerously-skip-permissions en ningún comando — usar siempre
  --allowedTools "mcp__ableton__*", que ya alcanza para esta sesión.

Verificación final antes de cerrar la sesión:
- node m4l-bridge/test-bridge.js corre sin error, JSON con is_error: false
- git status: m4l-bridge/ debe aparecer para commitear; nada de projects/ ni .claude/
- Commit: "feat: bridge Node for Max para invocar Claude Code (MCP ableton) desde M4L"
```

---

## Nota sobre el orden de sesiones

**Hacer primero:** KICKOFF A (git + README). El proyecto no existe públicamente hasta hacer este paso.
**Después:** KICKOFF B (refactor) — una vez el repo existe y es visible.
**Simultáneo con KICKOFF A:** grabar el demo GIF (DESIGN_TASKS.md DT1) si Ableton está abierto.
**Independiente, cuando quieras:** KICKOFF C (bridge M4L) — no depende de B, pero sí asume que A ya está hecho (necesita un repo real para el commit).
**Después de KICKOFF C, manual (no es una sesión de Claude Code):** DESIGN_TASKS.md DT4 — construir el patch `.amxd` en la GUI de Max apuntando al bridge ya creado y probado.
