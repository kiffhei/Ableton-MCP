# Ableton Live MCP Server

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

## Herramientas disponibles (19)

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
