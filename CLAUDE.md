# CLAUDE.md — Ableton Live MCP Server

MCP server en Python que conecta Claude Code con Ableton Live via AbletonOSC.
Controla Ableton en lenguaje natural: MIDI, progresiones musicales en cualquier
tonalidad y escala, gestión de proyectos, parámetros de instrumentos y efectos.

---

## Stack

- **Lenguaje:** Python 3.10+
- **Protocolo:** Model Context Protocol (MCP) via `mcp` SDK
- **Comunicación con Ableton:** AbletonOSC (Remote Script) via `python-osc`, puerto 11000
- **Persistencia:** JSON por proyecto en `projects/`

---

## Flujo de inicio

Al iniciar, ejecutar `list_projects` para ver proyectos existentes.

- **Si hay proyectos guardados:** preguntar si continúa el proyecto o es sesión nueva.
- **Si no hay proyectos:** recopilar datos (género, tonalidad, escala, BPM, estructura) y crear con `new_project`.

Preguntas necesarias para proyecto nuevo:
1. **Género** (ej: deep house, techno, hip-hop, afrobeats)
2. **Tonalidad** — nota raíz + modo mayor/menor (ej: D menor, F# mayor)
3. **Escala** — opcional (menor natural, dórica, frigia, blues, pentatónica)
4. **BPM**
5. **Estructura prevista** — opcional (intro+drop, 8 compases, canción completa)

---

## Herramientas disponibles (19 tools)

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

## Sistema de tonalidades y escalas

El motor calcula progresiones matemáticamente desde cualquier raíz.
Funciona con cualquier nota y cualquier escala.

Escalas disponibles:
- major / minor (natural)
- harmonic_minor / melodic_minor
- dorian / phrygian / lydian / mixolydian / locrian
- pentatonic_major / pentatonic_minor
- blues / whole_tone / diminished
- phrygian_dominant / hungarian_minor / double_harmonic

---

## Géneros disponibles (60+)

house, deep_house, afro_house, tech_house, garage_house,
techno, detroit_techno, industrial_techno, minimal_techno, melodic_techno,
trance, progressive_trance, psytrance, uplifting_trance,
drum_and_bass, liquid_dnb, neurofunk, jungle, halftime,
hip_hop, lo_fi, boom_bap, trap, drill, phonk,
rnb, neo_soul, funk, soul, gospel,
reggae, dancehall, dub,
jazz, jazz_fusion, bossa_nova, bebop, modal_jazz,
ambient, dark_ambient, idm, chillout, downtempo,
synthwave, darksynth, electro, future_bass, dubstep,
afrobeats, afrobeat, amapiano, baile_funk, cumbia, reggaeton,
rock, indie_rock, metal, doom_metal, post_rock,
cinematic, orchestral, neoclassical

---

## Referencia de instrumentos por rol

| Rol | Ableton sugerido | Alternativa |
|---|---|---|
| Bajo analógico | Analog | Operator |
| Bajo de sample | Simpler | Sampler |
| Pad / atmósfera | Wavetable | Operator |
| Lead sintetizador | Operator | Wavetable |
| Piano / keys | Sampler + sample | Grand Piano rack |
| Batería electrónica | Drum Rack | |
| Textura granular | Granulator II | Sampler |

---

## Flujo de clonado de canción real (MCP Spotify)

1. Buscar con `spotify_search`
2. Obtener audio features: key, mode, tempo, time_signature, energy
3. Mapear key numérico: 0=C 1=C# 2=D 3=D# 4=E 5=F 6=F# 7=G 8=G# 9=A 10=A# 11=B · mode: 1=major 0=minor
4. Construir patrón MIDI por conocimiento musical
5. Crear clip en Ableton con `add_midi_notes`
6. Sugerir instrumento con justificación

Nivel de fidelidad:
- 🟢 Alta — patrón muy documentado
- 🟡 Media — reconstrucción aproximada
- 🔴 Interpretación — canción poco documentada

---

## Reglas de comportamiento

### Siempre
- Índices base 0 para tracks y escenas
- Verificar `get_device_params` antes de `set_device_param`
- Reportar después de crear notas: track, escena, notas, duración
- Justificar la elección de instrumento

### Nunca
- No asumir que un device está cargado sin verificar
- No inventar parámetros OSC inexistentes en AbletonOSC
- No omitir el flujo de inicio si no hay contexto previo
