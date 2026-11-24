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

---

## Addendum 2 — 2026-06-25 (mismo día, sesión KICKOFF C)

**`set_track_volume` no tiene conversión determinística dB → valor de fader. El LLM la estima cada vez, con resultados distintos por sesión.**

Detectado al probar el bridge M4L: se pidió "sube el volumen a -6 dB" en dos sesiones distintas y el resultado fue diferente cada vez (`volume=0.75` una vez, `volume=0.426` otra; `-12 dB` dio `0.65` y luego `0.2135`).

**Causa raíz confirmada leyendo el código** (no es una hipótesis): la tool `set_track_volume` recibe el parámetro `volume` ya en escala 0.0–1.0, no en dB. La `description` da un solo punto de referencia ("0.85 = 0 dB") y ninguna fórmula. El handler hace `float(arguments["volume"])` y lo manda a OSC sin tocarlo. Cuando el usuario pide un valor en dB, es **Claude quien tiene que estimar mentalmente** la conversión con un solo punto de referencia — y por eso el resultado varía entre sesiones. No es un bug de OSC ni de Ableton: la tool nunca tuvo la conversión implementada.

**Por qué no hay una fórmula simple para "arreglarlo ya":** el mapeo real de Ableton no es logarítmico simple. Según discusión de desarrolladores de Max for Live, el tramo de -20dB a 0dB es lineal, pero el tramo por debajo de -20dB tiene una curva que ni la comunidad de M4L tiene documentada públicamente con precisión. Adivinar una fórmula aquí repetiría el mismo problema que estamos corrigiendo.

**Fix real recomendado (no hacer en esta sesión):** calibración empírica, no una fórmula adivinada:
1. En la UI de Ableton, ensanchar el mixer para mostrar la escala de dB junto al fader (función nativa de Live).
2. Mover el fader a 5-6 marcas conocidas (0, -6, -12, -20, -30, -60 dB) y leer el valor float real vía OSC (`/live/track/get/volume`) en cada una.
3. Construir una tabla de interpolación con esos pares (dB, float) reales — no estimados.
4. Cambiar el `inputSchema` de la tool para aceptar `db` directamente, y hacer la conversión en Python con esa tabla antes de llamar a OSC. El LLM deja de tener que adivinar nada.

**Tools potencialmente con el mismo patrón (sin confirmar todavía):** `set_track_pan` y `set_track_send` — ambas podrían tener el mismo problema de "descripción con un punto de referencia, sin conversión real". No verificado en esta sesión.

**Acción recomendada:** segundo GitHub Issue, separado del de endpoints OSC inexistentes — son dos clases de bug distintas (endpoint que no existe vs. conversión numérica nunca implementada).

---

## Addendum 3 — 2026-06-26 (sesión de cierre, bridge M4L en vivo)

**Observación abierta — cambio de volumen no confirmado en el track al usar el device.**

Probado el bridge M4L en vivo con el device "Claude Channel Strip.amxd" construido a mano en la misma sesión: se pidió cambiar el volumen de un track vía lenguaje natural desde el device. La tool respondió con mensaje de éxito, pero el fader del track que se estaba observando no cambió visualmente.

No se confirmó si el OSC llegó a un track distinto o si no llegó a ningún lado. Una hipótesis posible es off-by-one de índice: AbletonOSC es 0-indexado, por lo que si el `number box` del device tenía el valor `1`, el OSC apuntó al segundo track visual, no al primero. No se verificó el estado del segundo track en ese momento.

**Esta observación queda abierta.** No se puede concluir si es un bug del bridge, un error del usuario en el índice, o un problema de OSC.

**Próxima sesión:** reproducir el escenario con Ableton abierto, verificar el track inmediatamente después de pedir el cambio (revisar TODOS los tracks, no solo el esperado), y confirmar qué track_index recibió la acción — antes de descartar o confirmar como bug nuevo.

---

## Addendum 4 — 2026-07-21 (UI de Presentación del device M4L)

**Hallazgo al retomar DEV11:** el patch `.amxd` ya tenía `node.script` apuntando a `bridge-persistent.js` (la migración de DEV11 ya estaba hecha en el archivo real, aunque el checklist de DEV_TASKS.md la marcaba como pendiente — quedó desactualizado respecto al estado real del binario). Había además una conversación real guardada en el `comment` de salida, confirmando que el pipeline completo (`textedit` → `prepend ask`/`prepend track` → `node.script` → `route response` → `prepend set` → `comment`) funciona en vivo.

**Problema real reportado por el usuario:** ninguno de los tres objetos de interacción (`number` de track, `textedit` de prompt, `comment` de respuesta) tenía el atributo `presentation` activado, por lo que Ableton nunca los mostraba en la vista de Presentación del Device View — el único modo de usar el device era abrir el editor de Max (doble clic + ícono de lápiz), exactamente lo que el usuario quería evitar.

**Fix aplicado (fuera de la GUI de Max):** el `.amxd` resultó ser un contenedor binario trivial de 3 chunks (`ampf` + `meta` + `ptch`, cada uno `tag(4) + len_le(4) + payload`), donde el chunk `ptch` es JSON plano (patcher de Max) sin compresión. Se pudo editar con un script Python: se activó `presentation: 1` + `presentation_rect` en los 3 objetos existentes (sin tocar su wiring ni su lógica), se agregaron 3 labels `live.comment` nuevos ("Track:", "Instrucción:", "Respuesta:"), se seteó `openinpresentation: 1` a nivel patcher, y se limpió el texto de prueba dejado de la sesión anterior. Validado con round-trip completo (re-parseo del archivo escrito, objetos no tocados comparados byte-a-byte contra el original, IDs sin duplicados) antes de sobrescribir el archivo real.

**No verificado — requiere confirmación visual del usuario en Max/Ableton** (no hay forma de renderizar la GUI de Max de forma remota): que el device efectivamente abra en modo Presentación al insertarlo, que los 3 controles se vean sin abrir el editor, y que el dispositivo ya insertado en el Live Set actual necesite ser re-insertado (quitar y volver a arrastrar) para tomar el archivo `.amxd` actualizado, ya que Live no recarga en caliente el archivo de un device ya cargado.

**Bug encontrado tras la confirmación visual (texto garabateado):** el usuario confirmó que el device ya se ve en Presentación, pero el cuadro de respuesta mostraba el texto con la primera letra de casi cada palabra recortada. Causa identificada por comparación directa: los 3 labels nuevos usan `live.comment` (objeto nativo de Ableton) y se veían perfectos; el cuadro de respuesta heredado usaba `comment` clásico de Max, con un desajuste de ancho entre `patching_rect` (150px) y `presentation_rect` (270px). Fix: se convirtió ese cuadro a `live.comment`, se igualaron los anchos, se sacó un emoji del placeholder (no soportado por la fuente default de Max, se veía como un cuadrado), y se alineó el mismo desajuste de ancho en el `textedit` del prompt antes de que diera el mismo problema. Mismo método de edición directa del JSON, con el mismo round-trip de validación. No se puede confirmar visualmente sin que el usuario vuelva a mirar el device.

---

## Addendum 5 — 2026-07-21 (bridge-persistent.js sin scope, "se queda pasmado")

**Síntoma reportado:** al escribir instrucciones en el device ya funcional (Presentación + texto legible), el usuario percibía que "se queda pasmado" — la instrucción no parecía surtir efecto.

**Diagnóstico con evidencia reproducible:** se reprodujo el mismo flujo del bridge desde una terminal (mismo binario `claude`, mismos flags que usa `bridge-persistent.js`), con Ableton abierto. Confirmado:
1. El MCP server "ableton" del device que ya estaba corriendo en Ableton (proceso real, cadena Max → Node for Max → `claude -p` persistente → `server.py`) sí tenía el puerto OSC de recepción (11001) bindeado correctamente — la conexión OSC en sí no era el problema.
2. `bridge-persistent.js` lanzaba `claude` sin `--append-system-prompt` ni `--disallowedTools` — solo `--allowedTools mcp__ableton__*`, que **pre-aprueba pero no restringe**: el proceso heredaba el entorno personal completo del usuario (reglas globales de CLAUDE.md — TDD, HARD-GATE, agent-router por turno —, hooks de sesión, y decenas de tools genéricas). Para "sube el volumen del track 0 a -6 dB", el modelo terminó usando `Read`/`Grep` para explorar `track_tools.py` en vez de llamar la tool directamente — 10 turnos, 30+ segundos, sin resultado.
3. Nota metodológica: no se pudo probar contra el server.py real sin arriesgar un conflicto de puerto con el proceso ya activo del device del usuario — se usó una copia del `server.py` real (misma carpeta `src/`, mismos módulos hermanos, mismo `send_osc` real hacia Ableton) con `start_osc_listener()` deshabilitado, para poder testear en paralelo sin pisar el proceso en vivo. Esto significa que la prueba sí movió el volumen real del track 0 a -6 dB (0.65) en la sesión del usuario — cambio menor y fácilmente reversible, mencionado explícitamente al usuario.

**Fix aplicado:** se agregó a `bridge-persistent.js` un `--append-system-prompt` que instruye al modelo a actuar solo como controlador MCP directo (sin explorar, sin metodología de desarrollo), y un `--disallowedTools` explícito bloqueando Read/Grep/Glob/Bash/Write/Edit/Task/Skill/WebSearch y el resto de tools genéricas no relacionadas.

**Verificado (no en el device real, sí en el mecanismo):** con el fix, la misma instrucción se resolvió en **1 turno, ~9.5 segundos**, llamando `set_track_volume` directamente. Pendiente: el usuario debe quitar y volver a insertar el device (Max no recarga en caliente `bridge-persistent.js` mientras el proceso viejo sigue corriendo) para que tome el archivo corregido.

**Segundo bug encontrado al reinsertar el device — el real causante de "cada sesión que se inicie no tiene acceso al MCP":** al reinsertar el device para probar el fix anterior, apareció un mensaje del propio bridge diciendo que "esta sesión" no tenía las tools de Ableton cargadas. Diagnóstico confirmado con `ps`: había **dos cadenas completas Max → Node for Max → `claude -p` → `server.py` corriendo en paralelo** (PIDs de dos "Node for Max" runtimes distintos, 13497 y 14071). Node for Max **no mata el proceso `node.script` anterior cuando el device se saca del track** — la cadena vieja se queda viva, con el puerto OSC 11001 tomado; la cadena nueva (la que el usuario está usando) nunca logra bindear su propio `server.py` a ese puerto, así que su MCP "ableton" nunca conecta y sus tools nunca aparecen — sin ningún error visible en el device.

**Fix aplicado:** se mató manualmente la cadena vieja (PIDs 16156/16169) para desbloquear al usuario de inmediato, y se agregó a `bridge-persistent.js` una limpieza automática al arrancar: antes de lanzar su propio `claude`, corre `pkill -f ".../src/server.py"` (con una pausa breve para que el SO libere el puerto UDP) para matar cualquier huérfano de una carga anterior del device. Verificado en aislamiento (proceso decoy con el mismo path, `pkill` lo encontró y terminó, puerto liberado) — no se pudo probar el archivo `bridge-persistent.js` completo end-to-end porque requiere el módulo `max-api`, que solo existe corriendo dentro de Max.

**Pendiente de confirmación del usuario:** que al reinsertar el device una vez más, la nueva sesión sí tenga las tools `mcp__ableton__*` disponibles desde el primer intento.

---

## Addendum 6 — 2026-08-10 (pasada de vitrina)

**Contexto:** ejecución de VIT1, VIT2, VIT3 (checklist "Vitrina BA Automation" agregado
2026-08-07) y segunda pasada de DEV3, pendientes desde la auditoría de publicabilidad.
Cambios de documentación y empaquetado, sin tocar lógica de `src/*.py`.

**VIT1 — `pytest` ausente de `requirements.txt`:**
- Cambio: agregado `pytest>=8.0` a `requirements.txt`.
- Verificado con: `pytest tests/ -v` → **27 passed in 0.19s** (todas en `tests/test_music_theory.py`).
- Nota honesta: la verificación corrió con el pytest ya presente en el sistema (`/opt/anaconda3/bin/pytest`,
  Python 3.9.7), no en un venv limpio recién creado — se intentó instalar `requirements.txt`
  en un venv aislado (`python3 -m venv` + `pip install`) para replicar exactamente el
  escenario de "clon limpio", pero el `pip install` se colgó por timeout de red dos veces
  (2 min y 5 min) en este entorno y se abandonó. La corrección en sí (agregar la línea al
  archivo) es correcta y verificable por inspección; lo que no se pudo confirmar con
  evidencia fresca es el escenario exacto de "clon limpio + pip install" por una limitación
  del entorno de ejecución, no del cambio.

**VIT2 — rutas personales en `m4l-bridge/`:**
- Encontradas 6 ocurrencias de `/Users/brianear/...` en 4 archivos: `bridge-simple.js`,
  `bridge-persistent.js`, `test-bridge.js`, `test-persistent.js`.
- Cambio: las dos constantes (`CLAUDE_BIN`, `REPO_PATH` donde aplica) ahora se leen de
  `process.env.ABLETON_MCP_CLAUDE_BIN` y `process.env.ABLETON_MCP_REPO`, con fallback a
  placeholders evidentes (`REPLACE_WITH_CLAUDE_BIN_PATH`, `REPLACE_WITH_ABLETON_MCP_REPO_PATH`)
  en vez de una ruta hardcodeada de nadie en particular.
- Documentado en `m4l-bridge/README.md` (nuevo): qué variables exportar, cómo obtener sus
  valores (`which claude`, `pwd`), y la advertencia de que Max for Live lanzado desde
  Finder/Dock no siempre hereda el `$PATH`/entorno de un shell interactivo.
- Verificado con: `grep -rn "/Users/brianear" m4l-bridge/*.js` → sin resultados (exit 1).
- Para que el device de Max de Brian siga funcionando, Brian necesita exportar
  `ABLETON_MCP_CLAUDE_BIN` y `ABLETON_MCP_REPO` (en su `~/.zshrc` o en el entorno que Max
  hereda) — no es automático solo con este cambio. Queda anotado en el propio
  `m4l-bridge/README.md`.

**VIT3 — advertencia honesta al inicio del README:**
- Agregada nota de 3 líneas justo después del elevator pitch en `README.md`: requiere
  Ableton Live + AbletonOSC corriendo, sin modo demo ni mock headless.

**DEV3 (segunda pasada) — tabla del README desactualizada:**
- La tabla anterior documentaba 19 tools; el código real (`src/tool_definitions.py`) tiene 37.
- Reconstruida la tabla completa derivándola del código, no de documentación previa:
  37 esquemas en `tool_definitions.py`, agrupados por los 6 módulos de handlers
  (`transport_tools.py`, `clip_tools.py`, `device_tools.py`, `track_tools.py`,
  `project_tools.py`, `registry_tools.py`).
- Verificado con un script Python (AST) que extrae los nombres de `TOOL_DEFINITIONS` y los
  nombres de cada dict `HANDLERS` de los 6 módulos: **37 nombres en cada lado, `diff`
  vacío** — 37 tools ↔ 37 handlers, coincidencia exacta, sin huérfanos en ningún sentido.
  Repetido contra la tabla final del README (extraída con grep): también 37/37, `diff` vacío.
- Las 6 tools que llaman a endpoints OSC inexistentes en AbletonOSC estándar (`scan_plugins`,
  `build_plugin_registry`, `load_instrument`, `load_plugin`, `load_plugin_by_name`,
  `load_sample` — documentado arriba en este mismo archivo, auditoría original 2026-06-17)
  quedaron marcadas con ⚠️ en la tabla del README y con una nota al pie explicando que
  requieren extender el Remote Script. No se omitieron ni se presentaron como funcionales.
- Confirmado que la sección "Arquitectura" con el diagrama ASCII de DT2 (`DESIGN_TASKS.md`)
  ya existía en el README (agregada en una pasada anterior) — no hizo falta agregarla de nuevo.

**Qué queda sin resolver:** VIT4 (grabar un video/GIF corto del flujo funcionando) — no es
automatizable desde una sesión de Claude Code, requiere a Brian grabando su pantalla con
Ableton Live abierto.

---

## Addendum 7 — 2026-09-13 (base de conocimiento de herramientas gratuitas + prueba en vivo)

**Contexto:** se agregó `suggest_free_tool` — nueva tool MCP que recomienda herramientas
gratuitas de terceros (Max for Live devices, Live Extensions, plugins) desde
`tools_knowledge_base.json` antes de construir un recurso musical desde cero vía OSC.
8 herramientas registradas (verificadas como gratuitas contra su página real, no contra
suposiciones — 10 de las 16 originales del Linktree de sidebrain habían pasado a ser de
paga desde que se armó la lista de referencia). Módulos nuevos: `src/free_tools.py`,
`src/free_tools_handlers.py`. 40 tools totales, 53 tests pasando (`pytest`).

**Prueba en vivo pedida por el usuario:** cargar Call & Response Generator en un track
real ("Hard Techno Bass", 145 BPM) y no solo `suggest_free_tool`. Se encontraron dos
bugs reales en el camino:

**Bug 1 — `create_midi_track` reporta el nombre como aplicado sin aplicarlo.**
`create_midi_track(name="Hard Techno Bass")` devolvió confirmación de éxito con ese
nombre, pero `get_track_info` mostró el nombre por defecto de Ableton (`5-MIDI`).
`set_track_name` explícito sí funcionó. No investigado a fondo cuál handler genera el
mensaje sin verificar el resultado real — pendiente revisar `track_tools.py`/
`project_tools.py`.

**Bug 2 (más importante) — `scan_plugins`/`load_plugin` nunca encuentran nada puesto en
User Library.** Se copió `C&R Generator.amxd` a
`User Library/Presets/MIDI Effects/Max MIDI Effect/` con Live abierto; no aparecía en
`scan_plugins`. Hipótesis inicial (indexado en caliente) descartada reiniciando Ableton
por completo — seguía sin aparecer. Causa real, confirmada leyendo el Remote Script
extendido de AbletonOSC (`~/Music/Ableton/User Library/Remote Scripts/AbletonOSC/
abletonosc/track.py`, **no es parte de este repo**): los handlers
`/live/browser/scan`, `/live/browser/get/children`, `/live/browser/load` y
`/live/track/load_device` recorren `[instruments, plugins, audio_effects,
midi_effects, sounds, drums]` — `browser.user_library` nunca estaba en esa lista. La
ruta de samples (`track_load_sample`) sí la incluía (con `hasattr` de por medio); la de
devices, no.

**Fix aplicado:** se agregó `browser.user_library if hasattr(browser, 'user_library')
else None` (con `continue` si es `None`) a las 4 listas de categorías. Verificado con
`py_compile` antes de que el usuario reiniciara Ableton para cargar el Remote Script
parchado. Exportado como patch versionado en este repo —
`patches/abletonosc-browser-user-library.patch` + `patches/README.md` — porque la
carpeta de AbletonOSC no es un git repo y no está respaldada en ningún lado propio.

**Pendiente de confirmación:** reintentar `scan_plugins(filter="generator")` tras el
reinicio de Ableton y continuar la carga del device + instrumento de bajo en el track
si aparece. Detalle vivo en la memoria del proyecto (`pending-blockers.md` /
`conventions-learned.md` / `incidents-bugs.md`).

---

## Addendum 8 — 2026-09-13 (mismo día, cierre de la prueba en vivo: causa raíz v8ui + `get_clip_notes`)

**Continuación del Addendum 7.** Tras el patch de `browser.user_library`, `scan_plugins`
sí encontró "C&R Generator" y `load_plugin` lo cargó correctamente en el track (confirmado
con `get_track_devices`: `[00] C&R Generator (Max MIDI Effect)`, `[01] Analog
(UltraAnalog)`). `get_device_params` expuso 10 parámetros reales y automatizables
(Density, mutateAll, New Pair, Octave Jump, Octave, Randomize, Rate, Steps, live.dial).

**El device no renderiza su UI.** Captura de pantalla del usuario mostró el editor de Max
con un rectángulo rayado vacío y la etiqueta `(v8ui)` — el placeholder que Max dibuja
cuando un objeto de interfaz no logra instanciarse. Causa confirmada con evidencia dura,
no supuesta: el Max embebido en `Ableton Live 12 Suite.app/Contents/App-Resources/Max/
Max.app` es la **versión 8.6.0** (`CFBundleShortVersionString`), mientras que la propia
página de descarga de Cycling '74 (`cycling74.com/downloads`) lista **"Javascript V8
Integration (v8, v8ui, v8.codebox)" como novedad de Max 9** — exactamente el objeto que
usa este device. El producto ya declaraba "Max 9 o superior" como requisito en su propia
página de Gumroad, leída al inicio de esta sesión.

**Prueba definitiva de que no es solo cosmético:** se armó el track, se disparó grabación
de un clip vacío, se disparó el parámetro "New Pair" (ciclo 0→1→0, varias veces) mientras
grababa, se detuvo el clip, y se leyó su contenido con la tool nueva `get_clip_notes`
(ver abajo). El clip tenía 9 notas — pero el usuario confirmó que las escribió él mismo a
mano para comparar contra Analog, no el device. Sin la tool para leer el clip, esto se
habría dado por sentado como "sí generó algo". **Conclusión: el motor de generación de
Call & Response Generator no produce ninguna salida en Max 8.6** — no es solo la UI, es
la lógica completa (consistente con que la lógica probablemente vive dentro del mismo
script JS del `v8ui`, no en objetos Max clásicos separados).

**Alcance del problema — no es todo el feature de herramientas gratuitas:**
```bash
grep -al "v8ui" tools/*/*.amxd tools/*/*.ablx
```
Solo `call-response-generator/C&R Generator.amxd` usa `v8ui`. `MLR Live.amxd`,
`DrumSep...ablx` y `Styled Rhythm Generator...ablx` no lo usan — deberían funcionar sin
problema en Max 8.6. Roar Preset Pack y Granular Slicer son presets de devices nativos
de Live 12 (Roar, Granulator III), sin dependencia de Max for Live en absoluto.
Philodendron y Scintillate son plugins VST3/AU independientes de Max.

**Decisión del usuario:** no actualizar Ableton Live ni instalar Max 9 standalone
(experiencia previa de crash al subir de versión mayor; se ofreció la ruta de Max 9
standalone sin tocar Ableton, pero también se descartó). Call & Response Generator queda
documentado como **no utilizable en este equipo** hasta que eso cambie — no se intentó
ningún otro workaround técnico porque no existe uno: v8ui simplemente no está disponible
en Max 8.6.

**Tool nueva agregada a pedido del usuario: `get_clip_notes`.** El endpoint OSC
`/live/clip/get/notes` ya existía en AbletonOSC estándar (no es parte de la extensión
custom, confirmado en `clip.py` líneas 132-143) pero no estaba expuesto como tool MCP —
listado como pendiente en la memoria del proyecto desde hace tiempo. Implementado en
`clip_tools.py` siguiendo el mismo patrón de `get_device_params` (`send_osc` + leer
`osc_responses` con `osc_lock`, slice `[2:]` para descartar el eco de track/clip index),
agrupando la respuesta plana en notas de 5 campos (pitch, start_time, duration, velocity,
mute). Schema agregado en `tool_definitions.py`. 41 tools totales, 41 handlers, sin
huérfanos (verificado por consola). Probado en vivo contra el clip real del usuario:
leyó correctamente las 9 notas que él mismo había escrito a mano, con sus valores reales
de pitch/posición/duración/velocidad.

**Nueva regla en CLAUDE.md (a pedido explícito del usuario):** verificar con
`get_clip_notes` lo que un device realmente generó, en vez de asumir por el mensaje de
confirmación de la tool o por la descripción del producto — y, en general, si durante una
sesión se encuentra algo nuevo por adaptar o corregir (tool faltante, bug real, gap entre
lo documentado y lo real), implementarlo directamente en vez de solo reportarlo.

---

## 2026-11-24 — Base de conocimiento rítmica, y el error que la originó

### Qué se añadió

`knowledge/kick_bass_melodic_techno.json` + la tool `get_rhythm_pattern(genre, bpm)`
(`src/rhythm_tools.py`, 17 pruebas en `tests/test_rhythm_patterns.py`). 13 patrones de
bajo de melodic techno a 125 BPM, con su raíz medida y su procedencia.

### De dónde salen los datos

De la **rejilla MIDI mostrada en pantalla** en un anuncio del pack Arytmo "Melodic
Techno Kick & Bass" (grabación de 50.7 s), leída píxel a píxel: geometría de la
rejilla medida sobre el propio cuadro (114 px el compás 1, 615.5 el compás 2, 31.34 px
por 16avo) y alturas ancladas en la etiqueta "C" del teclado.

### El error que esto corrige, y por qué importa más que los datos

El análisis previo (`kick_bass_patterns.json`, 2026-11-22) tenía dos defectos que
conviene no repetir:

1. **Truncamiento silencioso.** El script imprimía `pb[:60]`: detectaba todos los
   onsets de los 50 s y guardaba `bass_t.npy` completo, pero solo los primeros 60
   llegaban al JSON. De ahí que documentara 4 compases de 26.
2. **Fuga de banda.** Filtraba `kick = band(x, 40, 120)` y `bass = band(x, 40, 250)`.
   La segunda contiene por completo a la primera, así que **cada golpe de kick se
   registró también como golpe de bajo**. En 3 de los 4 compases el patrón de kick
   resultaba ser un subconjunto completo del de "bajo".

La regla práctica: **en este registro no se puede separar kick de bajo por banda.** Las
raíces de los 13 loops caen entre 37 y 52 Hz, dentro de cualquier banda que capture el
kick. Quien lo intente otra vez obtendrá bajos que doblan el kick. Para separarlos hay
que ir a los armónicos del bajo (2º y 3º, por encima de 90 Hz) o a separación de fuentes.

Comprobación que lo delata en un vistazo: **ninguno de los 13 patrones reales toca en
los pasos 0, 4, 8 ni 12.** El bajo del JSON viejo sí lo hacía, en tres de cuatro
compases. Hay una prueba que lo fija (`test_el_bajo_nunca_pisa_un_tiempo_fuerte`).

### Límites de lo medido, declarados

- **Duraciones:** todas las notas son de un 16avo (bloques de 23-27 px sobre rejilla de
  31.34). Tampoco hay acentos por velocity: la desviación de color entre bloques es ~1
  de 255. Lo que se oye como notas más largas viene del envelope del instrumento.
- **Tonalidades:** el anuncio rotula una letra sin alteración. En 7 de 13 no coincide
  con la raíz leída, y las 7 discrepancias caen en teclas negras. Se conservan ambos
  datos; manda la medición.
- **Kick por loop:** no se extrajo. El piano roll del anuncio nunca lo muestra, y
  sacarlo del audio vuelve a chocar con la fuga de banda de arriba. Solo consta el 4 en
  el piso.
- **Cotejo con audio:** no concluyó (4-3 en una prueba A/B dirigida entre la raíz leída
  y la etiqueta del anuncio). La lectura visual se tomó como autoridad por tener error
  máximo de 1 px sobre 38.5 px por semitono, y por coincidir 13/13 entre dos métodos
  visuales independientes.
