# AUDIT.md — Ableton Live MCP Server
> Auditoría: 2026-06-17. Criterio: reclutador externo revisando repo en 5 minutos.

---

## 1. Funcionalidad — ¿corre end-to-end?

**BIEN:**
- Python compila sin errores de sintaxis
- 19 herramientas MCP implementadas (vs 7 en el README — doc drift severo)
- Motor de teoría musical completo: escalas, acordes, progresiones en cualquier tonalidad
- Persistencia de proyectos via JSON (directorio `projects/`)
- Integración Spotify descrita en CLAUDE.md para clonar canciones reales
- Sesión activa documentada (Digital Simbiosis, 8 escenas completas en D dórica 123 BPM)

**PROBLEMAS CRÍTICOS:**
- **No es un repositorio git.** No existe historial de commits, no hay URL de GitHub, no hay rama main. Para un reclutador, si no hay repo, el proyecto no existe. Es el bloqueo más severo de este proyecto para portafolio.
- **README documenta un subset menor del 37% de las capacidades reales.** El README lista 7 herramientas y 5 estilos. El server.py tiene 19 herramientas y el CLAUDE.md documenta 60+ géneros con progresiones por defecto.

---

## 2. Seguridad

**BAJO:**
- No hay secretos ni API keys en el código fuente (el MCP no los necesita)
- OSC en localhost (127.0.0.1) — no hay superficie de ataque de red
- `claude_mcp_config.json` usa `TU_USUARIO` como placeholder (correcto)

**PROBLEMAS:**
- **Ruta personal hardcodeada en CLAUDE.md:** `/Volumes/KiffHei/respaldo Mac 310523/playlist/samples/` — el nombre de la unidad y la ruta del backup son datos personales que no deben estar en un repo público. La ruta específica a samples también es sensible si se expone el directorio de proyectos.
- **Sin `.gitignore`:** cuando se inicialice git, el directorio `projects/` (con `digital-simbiosis/project.json` que contiene el estado de una producción real) quedará en el repo. Los proyectos musicales de producción son información privada.
- **CLAUDE.md** tiene el mismo riesgo que cafe-plus y harmony-lab: historial de sesiones de producción, lista de samples, equipamiento personal (Maschine, MiniFreak, MatrixBrute, KeyStep Pro) — información que no debería estar en un repo público.

---

## 3. Calidad de código

**BIEN:**
- Código Python idiomático: type hints, Path, asyncio, logging
- Separación clara entre OSC (comunicación), helpers musicales, y tools MCP
- `_active_project` como estado global con `global` explícito — es un pattern aceptable en scripts Python
- `build_progression` y `build_chord` son funciones puras bien estructuradas
- Manejo de errores en las tools (verificaciones de estado antes de actuar)

**PROBLEMAS:**
- **server.py tiene 1275 líneas.** El límite del proyecto es 800. La función `call_tool` concentra el dispatch de las 19 herramientas en un bloque `elif` de ~700 líneas — un lector externo ve un solo archivo monolítico.
- **Sin tests.** 1275 líneas de lógica musical (intervals, progressions, MIDI math) sin ningún test. Para un reclutador técnico que revisa el código, la ausencia de tests en una lógica matemática compleja es un red flag.
- **`call_tool` no tiene manejo de errores global.** Si un argumento falta o el type es inesperado, el server puede crashear silenciosamente. No hay un `try/except` wrapper.

---

## 4. Tests

**Estado:** 0 tests. Ningún archivo `.test.py` o `test_*.py` en el proyecto.

El motor musical (note_name_to_midi, scale_degree_to_root, build_chord, build_progression) es lógica matemática pura — ideal para unit tests. La ausencia total de tests en una herramienta de producción musical real contrasta con harmony-lab (489 tests del motor musical en JS).

Para portafolio, 10-20 tests de lógica pura demostrarían rigor técnico sin requerir Ableton instalado.

---

## 5. Documentación

**BIEN:**
- README cubre instalación, requisitos, configuración, ejemplos de uso
- CLAUDE.md exhaustivo con el sistema musical completo
- Instrucciones claras para conectar con AbletonOSC

**PROBLEMAS CRÍTICOS:**
- **README desactualizado.** El README lista 7 herramientas pero hay 19. Lista solo 5 géneros pero hay 60+. Las "tonalidades con progresiones predefinidas" son Am, Dm, Em, Cm, Fm, Gm — cuando en realidad cualquier tonalidad funciona porque el motor calcula por intervalos. Un reclutador que lea el README subestimará el proyecto por un factor de 3x.
- Sin badge de CI (no existe CI aún)
- Sin demo: no hay GIF, video, ni capturas de Claude controlando Ableton

---

## 6. UI/UX

No aplica — es un MCP server (herramienta de backend/integración, no tiene UI propia).

El "UX" es el flujo de prompts de Claude. El CLAUDE.md tiene un flujo bien definido. La experiencia real es: abrir Claude → Claude pregunta el género, tonalidad y BPM → crea los tracks automáticamente.

**Para portafolio:** un GIF de 30s mostrando Claude creando una progresión en Ableton en tiempo real tendría un impacto de portafolio enorme — nadie ha visto esto antes.

---

## 7. ¿Qué tan lejos está de "listo para mostrar"?

**Veredicto: 40% listo como portafolio, 90% listo como herramienta.**

Como herramienta: funciona. Brian lo usa para producción real (8 escenas completadas).

Como portafolio: el blocker principal es que no existe en GitHub. Sin repo, ningún reclutador puede ver el código. Los otros issues (README desactualizado, no tests) son secundarios pero severos.

**El concepto es el diferenciador más fuerte del portafolio:**
"Construí un MCP server que controla Ableton Live con lenguaje natural — crea progresiones en cualquier escala, maneja el estado de proyectos, y puede clonar la estructura musical de canciones reales vía Spotify."

Ese párrafo, con el código visible en GitHub, posiciona a Brian como alguien que entiende MCP (tecnología de 2025), producción musical, y automatización real. Para clientes de consultoría en n8n/automatización, es un diferenciador único.

---

## Addendum — 2026-06-25

**Bug de endpoints OSC inexistentes: creció de 4 a 6 tools.**

La auditoría original (2026-06-17) ya había detectado que `load_instrument`, `load_plugin`, `scan_plugins` y `load_sample` llaman a endpoints OSC que **no existen** en AbletonOSC estándar (`ideoforms/AbletonOSC`): `/live/track/load_device`, `/live/browser/scan`, `/live/track/load_sample`. Confirmado contra el código fuente de AbletonOSC y documentado externamente por otro proyecto MCP de Ableton, que señala que cargar dispositivos desde el Browser de Live requiere extender el Remote Script con un endpoint custom — no es parte de la API estándar.

Una sesión posterior (no commiteada hasta ahora) agregó `plugin_registry.py` y 18 tools nuevas (track/clip/scene control), pero **dos de las tools nuevas heredan el mismo bug**:

| Endpoint inexistente | Tools afectadas (6 total) |
|---|---|
| `/live/browser/scan` | `scan_plugins` (original), `build_plugin_registry` (nueva) |
| `/live/track/load_device` | `load_instrument`, `load_plugin` (originales), `load_plugin_by_name` (nueva) |
| `/live/track/load_sample` | `load_sample` (original) |

`build_plugin_registry` es la más grave de las dos nuevas: construye un registro completo de plugins instalados llamando a un endpoint que no existe, lo que significa que la funcionalidad central de "Plugins del usuario (preferidos)" documentada en `CLAUDE.md` probablemente no funciona contra una instalación estándar de AbletonOSC.

**Fix real (sin hacer todavía):** fork de AbletonOSC con un módulo `browser.py` que envuelva `Application.get_browser()` + `load_item()` de la Live Object Model — patrón ya usado en `track.py`/`device.py` del repo oficial.

**Acción recomendada:** abrir un GitHub Issue trackeando esto (`gh issue create`) en vez de dejarlo solo como nota en este archivo, ahora que el repo es público.
