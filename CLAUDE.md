# CLAUDE.md — Ableton Live MCP Server

MCP server en Python que conecta Claude Code con Ableton Live via AbletonOSC.
Controla Ableton en lenguaje natural: MIDI, progresiones musicales en cualquier
tonalidad y escala, gestión de proyectos, parámetros de instrumentos y efectos.

---

## Stack

- **Lenguaje:** Python 3.10+
- **Protocolo:** Model Context Protocol (MCP) via `mcp` SDK
- **Comunicación con Ableton:** AbletonOSC (Remote Script) via `python-osc`, puerto 11000
- **Persistencia:** JSON por proyecto en `projects/`, registry en `registry/plugins.json`

---

## Flujo de inicio

1. Ejecutar `list_projects` para ver proyectos existentes.
2. Si el registry de plugins está vacío (`get_ableton_version` lo indica), ejecutar `build_plugin_registry`.

- **Si hay proyectos guardados:** preguntar si continúa el proyecto o es sesión nueva.
- **Si no hay proyectos:** recopilar datos (género, tonalidad, escala, BPM, estructura) y crear con `new_project`.

Preguntas necesarias para proyecto nuevo:
1. **Género** (ej: deep house, techno, hip-hop, afrobeats)
2. **Tonalidad** — nota raíz + modo mayor/menor (ej: D menor, F# mayor)
3. **Escala** — opcional (menor natural, dórica, frigia, blues, pentatónica)
4. **BPM**
5. **Estructura prevista** — opcional (intro+drop, 8 compases, canción completa)

---

## Herramientas disponibles (37 tools)

### Plugins (nuevas)
| Herramienta | Descripción |
|---|---|
| `build_plugin_registry` | **Escanea Ableton y guarda TODOS los plugins instalados** — ejecutar una vez |
| `load_plugin_by_name` | Carga plugin por nombre: 'Maschine 2', 'Pigments', 'Reaktor 6', 'Orbit' |
| `search_plugin_registry` | Busca plugins en el registry local |

### Track Control (nuevas)
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

### Clip & Scene Control (nuevas)
| Herramienta | Descripción |
|---|---|
| `trigger_clip` | Dispara un clip en Session View |
| `stop_clip` | Detiene un clip |
| `trigger_scene` | Dispara una escena completa (fila) |

### Session (nuevas)
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

## Plugins del usuario (preferidos)

### Workflow con plugins
1. Primera vez: ejecutar `build_plugin_registry` con Ableton abierto (browser visible, tecla B)
2. Luego usar `load_plugin_by_name` con nombres amigables
3. Confirmar con `get_track_devices` y explorar con `get_device_params`

### Plugins favoritos documentados

| Plugin | Tipo | Rol principal | Cómo cargar |
|--------|------|---------------|-------------|
| **Maschine 2** (NI) | VST3 Instrument | Drum machines, samplers, texturas | `load_plugin_by_name("Maschine 2")` |
| **Arturia Pigments** | VST3 Instrument | Síntesis creativa, leads, pads, texturas | `load_plugin_by_name("Pigments")` |
| **Arturia AudioLab V** | VST3 Instrument | Síntesis clásica | `load_plugin_by_name("AudioLab V")` |
| **Reaktor 6** (NI) | VST3 Instrument | Síntesis avanzada, cajas de ritmo, texturas | `load_plugin_by_name("Reaktor 6")` |
| **Orbit** | VST3 Effect | Reverb/delay espacial, efectos atmosféricos | `load_plugin_by_name("Orbit")` |

### Roles sugeridos por instrumento

| Rol | Plugin preferido | Alternativa nativa |
|-----|------------------|--------------------|
| Caja de ritmos / grooves | Maschine 2 | Drum Rack |
| Texturas / ambient | Reaktor 6 | Granulator II |
| Síntesis creativa / pads | Arturia Pigments | Wavetable |
| Síntesis clásica / leads | Arturia AudioLab V | Operator |
| Efectos de espacio | Orbit | Reverb nativo |
| Bajo analógico | Analog (nativo) | Operator |
| Keys / piano | Electric (nativo) | Sampler + sample |

### Parámetros clave (explorar con get_device_params primero)

**Nota:** Los índices de parámetros varían entre versiones de plugin. Siempre ejecutar
`get_device_params` antes de `set_device_param` para confirmar los índices exactos en
la instalación de este equipo.

**Arturia Pigments — parámetros típicos a explorar:**
- Oscillator Type, Pitch, Wavetable Position
- Filter Cutoff, Filter Resonance
- Env Amount, Attack, Decay, Sustain, Release
- LFO Rate, LFO Amount
- FX: Chorus, Reverb, Delay

**Reaktor 6 — flujo recomendado:**
- Cargar con `load_plugin_by_name("Reaktor 6")`
- Usar `get_device_params` para ver qué ensemble está activo
- Los parámetros expuestos dependen del ensemble cargado

**Maschine 2 — flujo recomendado:**
- Principalmente controlado desde la interfaz de Maschine
- Para integración MIDI: crear track MIDI, cargar Maschine 2, armar el track
- Usar `arm_track` para habilitar grabación de MIDI desde Maschine

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

## Referencia de instrumentos nativos por rol

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

## Colores de referencia (RGB como entero)

| Color | Entero | Hex |
|-------|--------|-----|
| Rojo | 16711680 | #FF0000 |
| Naranja | 16744192 | #FF8000 |
| Amarillo | 16776960 | #FFFF00 |
| Verde | 65280 | #00FF00 |
| Cian | 65535 | #00FFFF |
| Azul | 255 | #0000FF |
| Magenta | 16711935 | #FF00FF |
| Blanco | 16777215 | #FFFFFF |
| Gris | 8421504 | #808080 |

---

## Reglas de comportamiento

### Siempre
- Índices base 0 para tracks y escenas
- Verificar `get_device_params` antes de `set_device_param`
- Verificar `get_track_devices` antes de modificar parámetros de un plugin
- Reportar después de crear notas: track, escena, notas, duración
- Justificar la elección de instrumento
- Si el usuario menciona un plugin por nombre → usar `load_plugin_by_name`
- Si el registry está vacío → ejecutar `build_plugin_registry` primero

### Nunca
- No asumir que un device está cargado sin verificar
- No inventar parámetros OSC inexistentes en AbletonOSC
- No omitir el flujo de inicio si no hay contexto previo
- No usar `load_plugin` con una URI inventada — siempre usar `scan_plugins` o `load_plugin_by_name`

### Flujo para cargar un plugin favorito
```
1. load_plugin_by_name(track_index=N, plugin_name="Maschine 2")
2. get_track_devices(track_index=N)  ← confirma que cargó
3. get_device_params(track_index=N, device_index=0)  ← explora parámetros
4. set_device_param(...)  ← ajusta según la necesidad
```
