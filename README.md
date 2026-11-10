# Ableton Live MCP Server

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MCP](https://img.shields.io/badge/MCP-Anthropic-orange)
![Ableton](https://img.shields.io/badge/Ableton%20Live-10%2F11%2F12-black)

> Controla Ableton Live con lenguaje natural via Claude Code.
> Motor de teoría musical para progresiones en cualquier tonalidad/escala,
> estado persistente de proyectos, y clonado de canciones reales vía Spotify.
> Construido con el Model Context Protocol (MCP) de Anthropic.

> **Requiere Ableton Live + AbletonOSC instalados y corriendo.** No hay modo
> demo ni mock headless — sin Ableton abierto, el MCP server no tiene con
> qué hablar y ninguna tool funciona.

---

## Arquitectura

```
Claude Code
    │
    │  MCP protocol (stdio)
    ▼
server.py (Python)
    │
    │  OSC messages → port 11000
    ▼
AbletonOSC (Remote Script)
    │
    │  Live Object Model API
    ▼
Ableton Live
         ▲
    projects/*.json
    (estado persistente)
```

---

## Requisitos

- macOS (donde corre Ableton)
- Ableton Live 10/11/12 con Max for Live
- Python 3.10+
- Claude Code (o claude.ai con MCP habilitado)

---

## Instalación

### 1. Instalar AbletonOSC en Ableton

```bash
git clone https://github.com/ideoforms/AbletonOSC.git
cp -r AbletonOSC ~/Music/Ableton/User\ Library/Remote\ Scripts/AbletonOSC
```

En Ableton: **Preferences → Link / Tempo / MIDI → Control Surface → AbletonOSC**

### 2. Instalar dependencias Python

```bash
cd ~/ableton-mcp
pip3 install -r requirements.txt
```

### 3. Configurar Claude Code

En `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ableton": {
      "command": "python3",
      "args": ["/Users/TU_USUARIO/ableton-mcp/src/server.py"],
      "env": {}
    }
  }
}
```

> Reemplaza `TU_USUARIO` con tu usuario de macOS (`whoami` en terminal)

### 4. Reiniciar Claude Code

Cierra y vuelve a abrir Claude Code. Verás `ableton` en la lista de MCP servers.

---

## Uso

Con Ableton abierto y AbletonOSC activo:

```
"Crea una progresión de deep house en Dm, escena 0"

"Haz un bassline de lo-fi en F# menor, octava 2"

"Cambia el BPM a 128"

"Clona la estructura armónica de 'Bohemian Rhapsody'"

"Carga un Analog en el track 3 y configura el sub como bass oscuro"
```

---

## Herramientas disponibles (40)

> Tabla derivada directamente del código (`src/tool_definitions.py` + los 7 módulos de
> handlers) — verificado 2026-09-13: 40 esquemas de tool ↔ 40 funciones registradas en
> `HANDLERS`, sin huérfanos en ningún sentido.
>
> Las filas marcadas **⚠️ requiere Remote Script extendido** llaman a endpoints OSC que
> **no existen** en AbletonOSC estándar (`ideoforms/AbletonOSC`) — ver nota al pie y
> `AUDIT.md`. No son aspiracionales ni están rotas por bug: fueron escritas asumiendo una
> API que el Remote Script estándar no expone. Funcionan solo si extiendes AbletonOSC con
> esos endpoints tú mismo.

### Transporte y sesión (`transport_tools.py`)
| Herramienta | Descripción |
|---|---|
| `set_tempo` | Cambia el tempo (BPM) del proyecto en Ableton |
| `play_pause` | Inicia o pausa la reproducción en Ableton (play/pause/stop) |
| `get_session_info` | Obtiene información del proyecto actual: BPM, tracks, escenas |
| `set_time_signature` | Cambia el compás del proyecto (ej: 4/4, 3/4, 6/8) |
| `get_ableton_version` | Versión de Ableton Live y estado de la conexión OSC |

### Progresiones y clips (`clip_tools.py`)
| Herramienta | Descripción |
|---|---|
| `add_chord_progression` | Genera una progresión de acordes MIDI según estilo, tonalidad y escala |
| `add_midi_notes` | Agrega notas MIDI individuales a un clip — basslines, melodías, secuencias custom |
| `set_clip_color` | Cambia el color de un clip en la Session View |
| `trigger_clip` | Dispara un clip en un slot de la Session View |
| `stop_clip` | Detiene un clip que está reproduciendo |
| `trigger_scene` | Dispara una escena completa (fila), todos sus clips a la vez |

### Devices y plugins (`device_tools.py`)
| Herramienta | Descripción |
|---|---|
| `load_instrument` | Carga un instrumento nativo de Ableton (analog, wavetable, drum_rack, etc.) ⚠️ requiere Remote Script extendido |
| `get_device_params` | Lee todos los parámetros de un device cargado en un track |
| `set_device_param` | Cambia un parámetro específico de un device |
| `set_device_params_bulk` | Cambia varios parámetros de un device en una sola llamada |
| `get_track_devices` | Lista los devices/plugins cargados en un track, con índice y tipo |
| `scan_plugins` | Escanea el browser de Ableton y lista plugins disponibles por URI ⚠️ requiere Remote Script extendido |
| `load_plugin` | Carga un plugin (VST3/VST2/AU/M4L) por URI exacta del browser ⚠️ requiere Remote Script extendido |
| `load_sample` | Carga un WAV/AIFF en el Simpler de un track ⚠️ requiere Remote Script extendido |

### Control de tracks (`track_tools.py`)
| Herramienta | Descripción |
|---|---|
| `create_midi_track` | Crea un nuevo track MIDI |
| `create_audio_track` | Crea un nuevo track de audio |
| `set_track_volume` | Volumen de track (0.0–1.0, 0.85 = 0 dB) |
| `set_track_pan` | Paneo (-1.0 izquierda, 0.0 centro, 1.0 derecha) |
| `set_track_mute` | Silencia o activa un track |
| `set_track_solo` | Activa o desactiva el solo de un track |
| `arm_track` | Arma o desarma un track para grabación |
| `set_track_name` | Renombra un track |
| `set_track_color` | Cambia el color de un track por RGB entero |
| `get_track_info` | Info completa de un track: nombre, vol, pan, mute, solo, arm, devices |
| `set_track_send` | Ajusta el nivel de envío de un track a un return track |

### Estado de proyecto (`project_tools.py`)
| Herramienta | Descripción |
|---|---|
| `new_project` | Crea un nuevo proyecto con carpeta de contexto (BPM, tonalidad, escala, género) |
| `load_project` | Carga el contexto de un proyecto existente al retomar una sesión |
| `save_project_state` | Guarda el estado actual del proyecto (tracks, devices, notas) |
| `list_projects` | Lista todos los proyectos guardados |

### Registry de plugins (`registry_tools.py`)
| Herramienta | Descripción |
|---|---|
| `build_plugin_registry` | Escanea el browser y construye un registro persistente de plugins instalados ⚠️ requiere Remote Script extendido |
| `load_plugin_by_name` | Carga un plugin por nombre en lenguaje natural ('Serum', 'Pigments'...) ⚠️ requiere Remote Script extendido |
| `search_plugin_registry` | Busca plugins en el registry local por nombre parcial |

### Herramientas gratuitas de terceros (`free_tools_handlers.py`)
| Herramienta | Descripción |
|---|---|
| `suggest_free_tool` | Busca en `tools_knowledge_base.json` una herramienta gratuita ya descargada que resuelva la tarea pedida, antes de construirla desde cero vía OSC |

---

**⚠️ Sobre las 6 tools marcadas "requiere Remote Script extendido":** `scan_plugins`,
`build_plugin_registry`, `load_instrument`, `load_plugin`, `load_plugin_by_name` y
`load_sample` llaman a los endpoints OSC `/live/browser/scan`, `/live/track/load_device`
y `/live/track/load_sample`, que **no existen** en AbletonOSC estándar
(`ideoforms/AbletonOSC`) — confirmado contra su código fuente. Cargar dispositivos o
samples desde el Browser de Live vía OSC requiere extender el Remote Script con
endpoints custom; no es parte de la API estándar. Contra una instalación de AbletonOSC
sin modificar, estas 6 tools no funcionan. Detalle completo en `AUDIT.md`.

---

## Motor de teoría musical

**60+ géneros** con progresiones características predefinidas:
house, deep_house, tech_house, afro_house, techno, minimal_techno,
hip_hop, lo_fi, trap, drill, boom_bap, rnb, neo_soul, jazz, jazz_fusion,
drum_and_bass, ambient, synthwave, afrobeats, amapiano, reggaeton, y más.

**Cualquier tonalidad y escala:**
cualquier nota (C, F#, Bb...) × cualquier escala (mayor, menor, dórica,
frigia, pentatónica, blues, doble armónica...).

---

## Base de conocimiento de herramientas gratuitas

`tools_knowledge_base.json` (raíz del proyecto) registra herramientas gratuitas de
terceros — Max for Live devices, Live Extensions, plugins VST/AU — ya descargadas en
`tools/<nombre>/`, cada una con su propio `README.md` (qué hace, requisitos, cómo se
instala/invoca).

**Regla del flujo de creación de canciones: antes de construir un recurso musical
desde cero vía OSC, consultar primero `suggest_free_tool`.** Si una herramienta
gratuita ya resuelve la tarea, se recomienda esa (con estado de instalación e
instrucciones) en vez de programar la solución desde cero. Ejemplos:

| Petición del usuario | Herramienta sugerida |
|---|---|
| "Dame un patrón rítmico complejo" | Styled Rhythm Generator (Lite) |
| "Separa este loop de batería en stems" | DrumSep |
| "Quiero variación melódica automática" | Call & Response Generator |
| "Necesito cortar este loop en slices para tocarlo en vivo" | MLR Live |
| "Dale textura/saturación a esta pista" | Roar Preset Pack |
| "Trocea este sample de forma granular" | Granular Slicer |
| "Quiero un efecto de freeze/glitch" | Philodendron |

Si `suggest_free_tool` no encuentra nada relevante, seguir con el flujo normal
(`add_chord_progression`, `add_midi_notes`, `generate_chord_progression`, etc.).

> **Nota — Scintillate:** el CDN de KVR (`static.kvraudio.com`) sirve el archivo detrás
> de un challenge de Cloudflare que solo un navegador resolviendo JS puede pasar; ni
> `curl` ni el sandbox de este proyecto pueden bajarlo automáticamente. Está registrado
> en la base de conocimiento (por si alguien más automatiza la descarga después) pero
> **el `.dmg` no está en `tools/scintillate/`** — bajar manualmente desde
> [kvraudio.com/product/scintillate-by-sweet-audio/downloads](https://www.kvraudio.com/product/scintillate-by-sweet-audio/downloads)
> y colocarlo ahí.

Herramientas registradas actualmente (todas verificadas como gratuitas al momento de
agregarlas — Gumroad/sitios de terceros cambian precios sin aviso, re-verificar antes
de asumir que algo sigue gratis):

| Herramienta | Categoría | Fuente |
|---|---|---|
| Call & Response Generator | sequencer | Side Brain (sidebrain.gumroad.com) |
| DrumSep | audio-tool | Side Brain |
| MLR Live | sequencer | Side Brain |
| Styled Rhythm Generator (Lite) | rhythm-generator | Side Brain |
| Roar Preset Pack (Free) | audio-tool | Side Brain |
| Granular Slicer | audio-tool | Side Brain |
| Philodendron | audio-tool | LNDF (lndf.fr) — no relacionado con Side Brain |
| Scintillate | audio-tool | Sweet Audio (kvraudio.com) — no relacionado con Side Brain, **descarga pendiente** (ver nota abajo) |

---

## Troubleshooting

**AbletonOSC no conecta:**
- Verifica que Ableton esté abierto antes de correr el MCP server
- Puerto 11000: `lsof -i :11000`

**Las notas no aparecen:**
- El track debe ser MIDI (no Audio)
- `track_index` y `scene_index` empiezan en 0

**Claude Code no ve el server:**
- Verifica la ruta en `claude_desktop_config.json`
- Test manual: `python3 src/server.py` (debe iniciar sin errores)

---

## Autor

Brian Eduardo Anaya Ruiz — Consultor de automatización  
[@kiffhei](https://github.com/kiffhei)
