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
