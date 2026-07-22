# DESIGN_TASKS.md — Ableton Live MCP Server | Tareas de diseño
> Este proyecto no tiene UI propia. Las tareas de "diseño" son de presentación y documentación visual.
> Fecha: 2026-06-17

---

## Estado de tareas (verificado contra el repo real — 2026-07-20)

- [ ] DT1 · Demo GIF para README
- [x] DT2 · Diagrama de arquitectura
- [x] DT3 · Badges para el README (completado 2026-07-20)
- [x] DT4 · Patch de Max for Live — "Claude Channel Strip" (completado 2026-06-25)

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

## DT4 · Patch de Max for Live — "Claude Channel Strip" `[COMPLETADO — 2026-06-25]`

**Por qué es manual:** Claude Code edita archivos y corre comandos, pero no tiene control de la interfaz gráfica de Max — no puede arrastrar objetos ni conectar cables en el patcher. El `.amxd` se construye a mano en la GUI de Max. El archivo resultante está respaldado en `m4l-bridge/device/Claude Channel Strip.amxd`.

**Receta validada (lo que realmente funciona):**

1. En Live: arrastra un **Max Audio Effect** vacío a cualquier canal → clic en el ícono de lápiz para abrir el editor.
2. Agregar un objeto `number` (para el track index) y un objeto `textedit` (para el prompt).
3. Conectar `number` → `prepend track` → inlet del `node.script`.
4. Conectar `textedit` → `prepend ask` → inlet del `node.script`.
5. Agregar objeto `node.script` con la ruta completa al bridge y **`@autostart 1`**:
   ```
   node.script /Users/brianear/proyectos/ableton-mcp/m4l-bridge/bridge-simple.js @autostart 1
   ```
6. Conectar la salida del `node.script` → `route response` → `prepend set` → `comment`.
7. Guardar como `Claude Channel Strip.amxd` en `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`.

**Errores encontrados en construcción (no en la receta original):**

- **CRÍTICO — `@autostart 1` es obligatorio.** Sin él el script nunca arranca y no hay ningún error visible: silencio total, ni siquiera un `print` de prueba produce salida. El único síntoma es que el device no responde a nada. La consola de Max NO muestra error por la ausencia de `@autostart 1`.
- **Typo: el objeto es `comment`, no `coment`.** El typo produce "No such object" en la consola de Max — fácil de cometer, fácil de diagnosticar.
- **Verificación de carga correcta:** la consola de Max debe mostrar la carga del script sin errores **inmediatamente** al confirmar la caja de `node.script`, sin necesidad de enviar ningún mensaje todavía.

**Troubleshooting:**

| Síntoma | Causa | Fix |
|---|---|---|
| `node.script: argument must be a <path>` | Falta la ruta al script o `@autostart 1` | Escribir la ruta completa + `@autostart 1` |
| Silencio total, device no responde | `@autostart 1` ausente | Agregar `@autostart 1` al objeto |
| "No such object" en consola | Typo en nombre de objeto (ej: `coment`) | Corregir a `comment` |

**Estado al cierre 2026-06-25:** device construido y funcionando en sesión en vivo. Pendiente confirmar comportamiento de índice de track (ver AUDIT.md Addendum 3).

**Actualización 2026-07-21 — UI de Presentación:** el `node.script` ya apuntaba a `bridge-persistent.js` (DEV11 estaba de hecho completo). El problema reportado por el usuario era otro: ningún objeto tenía `presentation: 1`, así que el device solo era usable abriendo el editor de Max. Se activó Presentación para el `number` (track), el `textedit` (prompt) y el `comment` (respuesta) editando el JSON del `.amxd` directamente (ver AUDIT.md Addendum 4 para el detalle técnico). Confirmado visualmente por el usuario: el device se ve en Presentación sin abrir el editor.

**Actualización 2026-07-21/22 — texto ilegible y bridge "pasmado":** dos bugs más encontrados y resueltos en la misma sesión, ambos con AUDIT.md Addendum 4/5 como detalle técnico completo:

1. **Texto garabateado en el cuadro de respuesta:** el cuadro heredado usaba `comment` clásico de Max en vez de `live.comment` (el objeto nativo que sí usan los labels), con un desajuste de ancho entre `patching_rect` y `presentation_rect`. Se convirtió a `live.comment` y se igualaron los anchos.
2. **El device "se quedaba pasmado" al recibir instrucciones:** dos causas combinadas —
   - `bridge-persistent.js` lanzaba `claude` sin system prompt ni restricción real de tools (`--allowedTools` solo pre-aprueba, no bloquea el resto), así que el modelo terminaba explorando el repo con `Read`/`Grep` en vez de llamar la tool MCP directamente.
   - Node for Max no mata el proceso `node.script` anterior cuando el device se saca del track — quedaban **dos cadenas Max→Node→claude→server.py corriendo en paralelo**, la vieja con el puerto OSC 11001 ocupado y la nueva sin poder conectar su propio MCP.

   Fix: `bridge-persistent.js` ahora lleva `--append-system-prompt` + `--disallowedTools` (bloqueando Read/Grep/Glob/Bash/Write/Edit/Task/Skill/WebSearch, etc.) para forzar acción directa, y una limpieza automática al arrancar (`pkill` sobre cualquier `server.py` huérfano de una carga anterior) para que cada inserción del device arranque con el puerto libre.

**Troubleshooting (actualizado):**

| Síntoma | Causa | Fix |
|---|---|---|
| `node.script: argument must be a <path>` | Falta la ruta al script o `@autostart 1` | Escribir la ruta completa + `@autostart 1` |
| Silencio total, device no responde | `@autostart 1` ausente | Agregar `@autostart 1` al objeto |
| "No such object" en consola | Typo en nombre de objeto (ej: `coment`) | Corregir a `comment` |
| Solo visible abriendo el editor de Max | Objetos sin `presentation: 1` | Activar Presentación + `presentation_rect` en cada objeto que deba verse en el Device View |
| Texto garabateado / letras faltantes en un cuadro | Objeto `comment` clásico (no `live.comment`) con `patching_rect` y `presentation_rect` de ancho muy distinto | Usar `live.comment` para texto en Presentación; igualar anchos de ambos rects |
| Device no responde o tarda 30+ seg sin resultado | `bridge-persistent.js` sin system prompt/tools restringidas → el modelo explora el repo en vez de llamar el MCP | `--append-system-prompt` + `--disallowedTools` forzando acción directa |
| "Esta sesión no tiene las tools de Ableton" en la respuesta | Proceso `server.py` huérfano de una carga anterior del device ocupando el puerto OSC 11001 | `bridge-persistent.js` ahora mata huérfanos (`pkill`) antes de arrancar el suyo — si igual pasa, matar servers.py viejos a mano y reinsertar el device |
