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

## Herramientas disponibles (44 tools)

Ver tabla completa en `README.md` — ahí sirve porque la leen los usuarios
finales del MCP, que no ven el schema. El schema MCP ya expone las 44 tools
en tiempo de ejecución.

---

## Plugins del usuario (preferidos)

Lista completa en memoria del proyecto:
`~/.claude/projects/-Users-brianear-proyectos-ableton-mcp/memory/user_prefs.md`

Workflow: `build_plugin_registry` (una vez) → `load_plugin_by_name` con nombre
amigable → confirmar con `get_track_devices` y explorar con `get_device_params`.

---

## Sistema de tonalidades y escalas

Ver skill `.claude/skills/tonalidades-escalas/SKILL.md`.

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

Ver skill `.claude/skills/instrumentos-por-rol/SKILL.md`.

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

## Devices Max for Live de este repo

Antes de tocar o construir cualquier device M4L (bridge, C&R Generator, o uno
nuevo): leer `docs/M4L_DEVICE_GUIDE.md`. Cubre reglas de layout verificadas con
feedback real (horizontal no vertical, qué controles necesitan su propia
etiqueta), dónde vive de verdad el rango de automatización (no son los atributos
de nivel superior), el `.amxd` como JSON editable sin GUI, y las dos causas reales
de "cada sesión es un pedo" con el bridge MCP (puertos huérfanos, modelo
explorando el repo en vez de llamar el MCP directo).

## Herramientas gratuitas de terceros

Antes de construir un recurso musical desde cero vía OSC (ritmo complejo, separación
de stems, variación melódica, live-looping por slices, efectos granulares/glitch),
llamar primero `suggest_free_tool(task_description)`. Registro completo en
`tools_knowledge_base.json`, herramientas descargadas en `tools/<nombre>/` con su
propio README. Detalle y tabla de ejemplos en `README.md` → "Base de conocimiento de
herramientas gratuitas".

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

> `CLAUDE.md` es la fuente de verdad para "Reglas de comportamiento" — la versión
> en `CLAUDE.internal.md` quedó desactualizada (no cubre plugin registry ni
> `load_plugin_by_name`) y fue reemplazada ahí por un puntero a esta sección.

### Siempre
- Índices base 0 para tracks y escenas
- Verificar `get_device_params` antes de `set_device_param`
- Verificar `get_track_devices` antes de modificar parámetros de un plugin
- Reportar después de crear notas: track, escena, notas, duración
- Justificar la elección de instrumento
- Si el usuario menciona un plugin por nombre → usar `load_plugin_by_name`
- Si el registry está vacío → ejecutar `build_plugin_registry` primero
- Verificar con `get_clip_notes` lo que un device realmente generó en un clip — no
  asumir por el mensaje de confirmación de la tool que lo disparó, ni por lo que
  debería hacer según su descripción (ver caso Call & Response Generator, AUDIT.md
  Addendum 7)
- **Si se encuentra algo nuevo por adaptar o corregir mientras se trabaja** (una tool
  que falta, un bug real, un gap entre lo documentado y lo que realmente pasa),
  implementarlo directamente en vez de solo reportarlo y dejarlo pendiente — siempre
  que sea una corrección viable dentro del alcance de la sesión

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
