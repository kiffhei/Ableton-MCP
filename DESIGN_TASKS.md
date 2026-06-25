# DESIGN_TASKS.md — Ableton Live MCP Server | Tareas de diseño
> Este proyecto no tiene UI propia. Las tareas de "diseño" son de presentación y documentación visual.
> Fecha: 2026-06-17

---

## DT1 · Demo GIF para README `[ALTA — máximo impacto de portafolio]`

**Qué grabar (30-45 segundos):**
1. Ventana de Claude Code con el MCP conectado
2. Escribir: "Haz una progresión de deep house en Dm, escena 0"
3. Claude ejecuta las herramientas MCP en tiempo real (se ven los llamados)
4. Ableton Live muestra el clip creado y los MIDI notes apareciendo
5. Reproducir el clip (se escucha el resultado)

**Herramientas:**
- QuickTime Player → File → New Screen Recording (seleccionar solo las 2 ventanas)
- Para convertir a GIF: `ffmpeg -i demo.mov -vf "fps=15,scale=800:-1" demo.gif`
- O usar Gifox (app de Mac, graba directamente como GIF con compresión)

**Dónde guardar:** `docs/demo.gif` en el repo. Agregar al README:
```md
## Demo

![Claude controlando Ableton en tiempo real](docs/demo.gif)
```

---

## DT2 · Diagrama de arquitectura `[MEDIA]`

Agregar al README sección "Arquitectura":

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
```

Formato: diagrama ASCII en bloque de código en el README. Simple, claro, no requiere herramientas externas.

---

## DT3 · Badges para el README `[BAJA]`

Una vez el repo esté en GitHub con CI básico:
```md
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![MCP](https://img.shields.io/badge/MCP-Anthropic-orange)
![Ableton](https://img.shields.io/badge/Ableton%20Live-10%2F11%2F12-black)
```

Los badges de tecnología no requieren CI — son estáticos y se agregan manualmente.

---

## DT4 · Patch de Max for Live — "Claude Channel Strip" `[ALTA — manual, NO delegable a Claude Code]`

**Por qué es manual:** Claude Code edita archivos y corre comandos, pero no tiene control de la interfaz gráfica de Max — no puede arrastrar objetos ni conectar cables en el patcher. El `.amxd` se construye a mano en la GUI de Max (~10-15 min), mientras que todo el código (los bridges de DEV7) sí lo hace Claude Code.

**Pasos:**
1. En Live: arrastra un **Max Audio Effect** vacío a cualquier canal → clic en el ícono de lápiz para abrir el editor.
2. Agregar objeto `live.path` con mensaje `path this_device canonical_parent` disparado por `loadbang` → resuelve el track donde vive el device.
3. Conectar la salida a un `live.object` con mensaje `path`, y pasar el resultado por un `regexp` (patrón `tracks (\d+)`) para extraer el número de track.
4. Agregar `live.text` o `textedit` para escribir el prompt.
5. Agregar `node.script` apuntando a `m4l-bridge/bridge-simple.js` (cambiar a `bridge-persistent.js` después de DEV11). Conectar: track_index + texto → mensaje `ask <track_index> <prompt>` al inlet de `node.script`.
6. Conectar la salida `response` del `node.script` a un `comment` o `live.text` en modo display.
7. Guardar como `Claude Channel Strip.amxd` en `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`.

**Verificación:** arrastra el device a un track distinto al original — el track_index mostrado debe actualizarse solo, sin reconfigurar nada.
