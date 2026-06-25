# MASTER PLAN — Ableton MCP: Plugin Discovery + Full Control
> Auditoría: 2026-06-18 | Objetivo: control total de Ableton + plugins del usuario en lenguaje natural

---

## AUDITORÍA: Qué falta para el objetivo real

### CRÍTICO — Sin esto el objetivo no se cumple

**C1 · Plugin Registry (lista exacta de plugins instalados)**
- `scan_plugins` actual usa `/live/browser/scan` solo como búsqueda ad-hoc — no hay registro persistente
- No existe `load_plugin_by_name` — requiere URI exacta, no nombre humano
- Los plugins favoritos (Maschine 2, Pigments, Reaktor 6, Orbit) no están documentados en CLAUDE.md
- Sin registry, Claude no puede decir "carga Maschine 2 en el track 1" sin saber la URI

**C2 · Herramientas de track faltantes (15+ funciones de Ableton sin cobertura)**
- Volume, pan, mute, solo, arm — fundamentales, no existen en el MCP
- Rename track, set track color — sin ellos no se puede organizar visualmente
- No hay `create_audio_track` — solo MIDI
- No hay `trigger_clip` / `stop_clip` / `trigger_scene` — sin control de reproducción de clips
- No hay `set_track_send` — sin manejo de envíos a returns

**C3 · Detección de versión de Ableton**
- El MCP no sabe qué versión de Live está instalada
- Algunos comandos OSC varían entre Live 11/12 — sin detección puede enviar comandos incorrectos

**C4 · CLAUDE.md no documenta plugins del usuario**
- Nada sobre Maschine 2, Arturia Pigments, Reaktor 6, Orbit
- Sin presets de parámetros para plugins favoritos
- Sin workflow de cómo descubrir URIs y usarlos

---

### IMPORTANTE — Mejora la experiencia sustancialmente

**I1 · Plugin parameter maps para plugins favoritos**
- Documentar índices de parámetros clave de Maschine 2, Pigments, Reaktor 6, Orbit
- Permite decir "sube el cutoff de Pigments" → sabe qué param_index usar

**I2 · Herramientas de clip y arrangement faltantes**
- `quantize_clip` — cuantizar notas de un clip
- `duplicate_clip` — duplicar clip a otro slot
- `set_clip_loop` — definir loop points de un clip
- `set_clip_pitch` — transposición de clip
- `get_clip_notes` — leer notas de un clip existente

**I3 · Control de returns y master**
- `get_return_tracks` — listar return tracks
- `set_master_volume` / `get_master_volume`
- `set_crossfader` — control del crossfader

---

### FASES DE EJECUCIÓN

#### FASE 1: Plugin Registry System [EJECUTANDO]
- [ ] Crear `src/plugin_registry.py` — módulo de gestión de registry
- [ ] Agregar `build_plugin_registry` tool en server.py — crawlea el browser y guarda JSON
- [ ] Agregar `load_plugin_by_name` tool — resuelve nombre a URI y carga
- [ ] Crear `registry/` directory + `.gitkeep`
- [ ] Actualizar CLAUDE.md con sección de plugins del usuario

#### FASE 2: Track Control Tools
- [ ] `set_track_volume` / `set_track_pan`
- [ ] `set_track_mute` / `set_track_solo` / `arm_track`
- [ ] `set_track_name` / `set_track_color`
- [ ] `get_track_info` — resumen completo de un track
- [ ] `set_track_send`
- [ ] `create_audio_track`

#### FASE 3: Clip & Scene Control
- [ ] `trigger_clip` — disparar un clip slot
- [ ] `stop_clip` — detener un clip slot
- [ ] `trigger_scene` — disparar una fila completa
- [ ] `get_clip_notes` — leer notas existentes

#### FASE 4: Ableton Version & Advanced
- [ ] `get_ableton_version` — detecta versión de Live
- [ ] `set_time_signature`
- [ ] `duplicate_clip`
- [ ] `quantize_clip`

#### FASE 5: CLAUDE.md Full Update
- [ ] Sección plugins del usuario con workflow completo
- [ ] Plugin parameter maps conocidos
- [ ] Workflow build_plugin_registry al inicio
- [ ] Track control reference
- [ ] Scene/clip control reference

---

## Plugins del usuario (documentados por él)

| Plugin | Tipo | Uso |
|--------|------|-----|
| Maschine 2 (NI) | VST3 Instrument | Drum machines, texturas, samplers |
| Arturia Pigments | VST3 Instrument | Síntesis creativa, leads, pads |
| Arturia AudioFuse V (AudioLab V) | VST3 Instrument | ? |
| Reaktor 6 (NI) | VST3 Instrument | Síntesis avanzada, texturas |
| Orbit | VST3 Effect | Efecto de espacio/reverb/delay |
| Efectos nativos Ableton | Built-in | Compresores, EQs, reverbs, etc. |

---

## Estado de fases
- FASE 1: [x] COMPLETADA — Plugin Registry System (build_plugin_registry, load_plugin_by_name, search_plugin_registry)
- FASE 2: [x] COMPLETADA — Track Control (10 tools: vol, pan, mute, solo, arm, name, color, info, send, audio track)
- FASE 3: [x] COMPLETADA — Clip & Scene Control (trigger_clip, stop_clip, trigger_scene)
- FASE 4: [x] COMPLETADA — Session tools (set_time_signature, get_ableton_version)
- FASE 5: [x] COMPLETADA — CLAUDE.md actualizado con plugins del usuario y workflow completo

## Resultado: 37 tools | Compilación: OK | Handlers: 100% cubiertos
