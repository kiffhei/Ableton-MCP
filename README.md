# Ableton Live MCP Server

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MCP](https://img.shields.io/badge/MCP-Anthropic-orange)
![Ableton](https://img.shields.io/badge/Ableton%20Live-10%2F11%2F12-black)

> Controla Ableton Live con lenguaje natural via Claude Code.
> Motor de teoría musical para progresiones en cualquier tonalidad/escala,
> estado persistente de proyectos, y clonado de canciones reales vía Spotify.
> Construido con el Model Context Protocol (MCP) de Anthropic.

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

## Herramientas disponibles (37)

### Plugins
| Herramienta | Descripción |
|---|---|
| `build_plugin_registry` | **Escanea Ableton y guarda TODOS los plugins instalados** — ejecutar una vez |
| `load_plugin_by_name` | Carga plugin por nombre: 'Maschine 2', 'Pigments', 'Reaktor 6', 'Orbit' |
| `search_plugin_registry` | Busca plugins en el registry local |

### Track Control
| Herramienta | Descripción |
|---|---|
| `set_track_volume` | Volumen de track (0.0–1.0, 0.85 = 0 dB) |
| `set_track_pan` | Paneo (-1.0 izquierda, 0.0 centro, 1.0 derecha) |
| `set_track_mute` | Mutear/desmutear track |
| `set_track_solo` | Solo/unsolo track |
| `arm_track` | Armar track para grabación |
| `set_track_name` | Renombrar track |
| `set_track_color` | Color de track por RGB entero |
| `get_track_info` | Info completa: vol, pan, mute, solo, arm, devices |
| `set_track_send` | Nivel de envío a return track |
| `create_audio_track` | Crea track de audio |

### Clip & Scene Control
| Herramienta | Descripción |
|---|---|
| `trigger_clip` | Dispara un clip en Session View |
| `stop_clip` | Detiene un clip |
| `trigger_scene` | Dispara una escena completa (fila) |

### Session
| Herramienta | Descripción |
|---|---|
| `set_time_signature` | Cambia el compás (ej: 4/4, 3/4, 6/8) |
| `get_ableton_version` | Versión de Live + estado del registry |

### Originales
| Herramienta | Descripción |
|---|---|
| `add_chord_progression` | Genera progresiones en cualquier tonalidad y escala |
| `add_midi_notes` | Agrega notas MIDI individuales con control total |
| `create_midi_track` | Crea un nuevo track MIDI |
| `set_tempo` | Cambia el BPM del proyecto |
| `play_pause` | Controla reproducción (play/pause/stop) |
| `get_session_info` | Info del proyecto: tracks, escenas, BPM |
| `set_clip_color` | Colorea clips por índice RGB |
| `load_instrument` | Carga instrumento nativo de Ableton |
| `load_plugin` | Carga plugin por URI exacta |
| `load_sample` | Carga WAV/AIFF en Simpler |
| `get_device_params` | Lee parámetros de un device/plugin |
| `set_device_param` | Modifica un parámetro específico |
| `set_device_params_bulk` | Modifica múltiples parámetros a la vez |
| `get_track_devices` | Lista devices de un track |
| `scan_plugins` | Escanea browser de Ableton |
| `new_project` | Crea proyecto con estado persistente |
| `load_project` | Carga proyecto existente |
| `save_project_state` | Guarda estado del proyecto |
| `list_projects` | Lista proyectos guardados |

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
