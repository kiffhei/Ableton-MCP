# Guía de diseño — devices Max for Live de este repo

> Documento consolidado, pedido explícitamente por Brian el 2026-11-10 porque la
> GUI de Max nunca salía bien a la primera y porque cada sesión nueva del bridge MCP
> repetía fricciones ya resueltas antes. Esto es la síntesis **operativa** — el
> detalle forense completo de cada bug sigue en `AUDIT.md` (Addendums 3-8) y
> `DESIGN_TASKS.md` (DT4); aquí solo está lo que hay que saber ANTES de tocar o
> construir un device nuevo, para no repetir el mismo descubrimiento por las malas.
>
> Claude Code no controla la GUI de Max — no arrastra objetos ni conecta cables a
> mano. Todo lo de abajo se hace editando el `.amxd` directamente (es un JSON, ver
> §3) o generándolo con `py2max` (ver `max-device/build_device.py`). La única parte
> que de verdad requiere ojos humanos es confirmar visualmente el resultado en Live.

## 0. Qué devices existen aquí

| Device | Dónde vive | Qué hace | Estado real |
|---|---|---|---|
| **Claude Channel Strip** | `m4l-bridge/` (`.amxd` en `~/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect/`) | Bridge: escribe un prompt + track index, Node for Max lanza `claude -p` apuntando al MCP de este repo, la respuesta vuelve al device. | Funciona en vivo, confirmado por Brian. Ver §4 para las fricciones de sesión-a-sesión. |
| **C&R Generator (rebuild)** | `max-device/` (instalado en `~/Music/Ableton/User Library/Presets/MIDI Effects/Max MIDI Effect/CR_Generator_rebuild.amxd`) | Generador propio de frases "Call & Response" (puerto ES5 del motor MIT de Nordl3), reemplazo del device de Side Brain que no corre en este Max 8.6 (usa `v8ui`, requiere Max 9). | Patcher construido e iterado visualmente con `py2max`. **La generación de notas nunca se verificó de punta a punta** (correr `get_track_devices` → `get_device_params` → disparar `New Pair`/`Write Clip` → `get_clip_notes` antes de asumir que funciona). |

Cualquier device M4L **nuevo** en otro proyecto (p. ej. `orbit-poly`) hereda las
reglas de las secciones 1-3 — son de Max for Live en general, no de este repo.

## 1. Reglas de layout visual (feedback real de Brian, no intuición)

Fuente: `max-device/build_device.py` (comentarios inline) + iteración en vivo del
device C&R Generator.

- **Horizontal, no vertical.** Primer intento: secciones apiladas con encabezados.
  Feedback real: *"no distribuyas hacia abajo, hazlo hacia la derecha mejor"*.
  Layout correcto: filas anchas (menús / menús / dials+botones), columnas dentro de
  cada fila — no una columna larga de secciones con título.
- **`live.dial` / `live.slider` / `live.numbox` ya traen su propio nombre + valor**
  dibujado debajo del widget en el panel de Ableton. Agregarles un `comment` propio
  arriba **duplica la etiqueta** — reportado como *"se enciman etiquetas"*. Solo
  `live.menu` y `live.button` (que no traen etiqueta propia) necesitan un `comment`
  aparte.
- **La franja de nombre+valor de `live.dial` no está contada en su alto (`ctl_h`).**
  Si la siguiente fila empieza justo después del alto nominal del dial, su label se
  encima con esa franja (pasó con "Pattern" encimándose con el valor de "Octave").
  Dejar margen extra después de cualquier fila con `live.dial`.
- **`live.button` es un LED pequeño sin texto propio** — casi invisible en el panel
  si no lleva un `comment` con su nombre justo encima, estilo macro de Ableton
  (nombre chico arriba, control debajo).
- **Vista de solo-lectura (ej. un `multislider` tipo step-sequencer) no es un
  parámetro `live.*`** — se actualiza empujando valores por nombre con `messnamed`
  desde el `js`, nunca participa de la automatización.

## 2. Automatización real — dónde vive el rango, de verdad

Los atributos de nivel superior de un `live.dial`/`live.numbox`/`live.menu`
(`min`, `max`, `items`...) **solo gobiernan el widget dentro del editor de Max**.
Lo que Live expone al Live Object Model y a la automatización sale de
`saved_attribute_attributes.valueof`:

```python
valueof = {
    'parameter_longname': label,
    'parameter_shortname': label[:8],
    'parameter_type': param_type,     # si aplica
    'parameter_mmin': param_min,      # NO "min"
    'parameter_mmax': param_max,      # NO "max"
    'parameter_enum': param_enum,     # para live.menu — NO "items"
}
ctl = p.add_textbox(maxclass, ..., saved_attribute_attributes=dict(valueof=valueof))
```

Sin este bloque, todo dial/numbox cae al rango default 0-127 y todo `live.menu`
cae a una lista vacía — **aunque el widget se vea bien en el editor de Max**. Esto
es la causa más probable si un control "se ve bien pero no automatiza/no tiene las
opciones correctas" al insertarse en Live.

## 3. El `.amxd` es un JSON editable — no hace falta la GUI para todo

Contenedor binario trivial de 3 chunks: `ampf` + `meta` + `ptch`, cada uno
`tag(4) + len_le(4) + payload`. El chunk `ptch` es el patcher completo como **JSON
plano sin comprimir**. Por eso se puede:

- Activar `presentation: 1` + `presentation_rect` en un objeto existente sin tocar
  su wiring ni su lógica (así se arregló que el bridge solo fuera usable abriendo
  el editor de Max — Addendum 4).
- Convertir un `comment` clásico a `live.comment` cuando el texto se ve
  "garabateado" en Presentación (desajuste `patching_rect` vs `presentation_rect`,
  o fuente que no soporta un carácter como un emoji).
- Construir un patcher nuevo de cero con `py2max` (`max-device/build_device.py`) en
  vez de editar JSON a mano — mejor para devices con muchos controles repetidos.

**Protocolo obligatorio antes de sobrescribir un `.amxd` real:** parsear el
resultado de vuelta, comparar byte-a-byte los objetos que NO se tocaron contra el
original, confirmar que no hay IDs duplicados. Nunca sobrescribir a ciegas.

**Live NO recarga en caliente un `.amxd` ya insertado en el Live Set.** Después de
editar el archivo, el device necesita ser **quitado y vuelto a arrastrar** al track
para tomar la versión nueva — si algo "no cambió" tras un fix, esto es lo primero
que hay que descartar antes de asumir que el fix no funcionó.

## 4. Continuidad entre sesiones del bridge MCP (la queja de "cada sesión es un pedo")

Dos causas reales ya diagnosticadas — revisar esto ANTES de asumir que algo se
rompió de nuevo sin razón:

1. **Puertos huérfanos.** Node for Max no mata el proceso `node.script` anterior
   cuando el device se saca del track — puede quedar una cadena vieja
   Max→Node→`claude`→`server.py` viva, con el puerto OSC 11001 ocupado, mientras la
   cadena nueva nunca logra bindear el suyo (sin ningún error visible en el
   device). `bridge-persistent.js` ya corre `pkill -f ".../src/server.py"` al
   arrancar — si el síntoma reaparece, verificar a mano:
   ```bash
   ps aux | grep server.py
   lsof -i :11001
   ```
   antes de tocar código.
2. **El modelo explorando en vez de llamar el MCP directo.** Si el bridge se
   lanzara sin `--append-system-prompt` + `--disallowedTools`, el proceso hereda el
   entorno personal completo (reglas globales, hooks, decenas de tools genéricas) y
   el modelo puede terminar usando `Read`/`Grep` para explorar el repo en vez de
   llamar la tool MCP directamente — 10 turnos y 30+ segundos para algo que son
   1 turno y ~9.5 segundos con el scope correcto. Si una instrucción simple tarda
   mucho o "no hace nada", confirmar que `bridge-persistent.js` sigue teniendo esos
   dos flags antes de rediagnosticar desde cero.

**Checklist al reinsertar el device tras cualquier cambio:**
1. ¿Se mató el proceso viejo (`pkill`) o se confirmó que no hay huérfano?
2. ¿El device se quitó y se volvió a arrastrar (no solo se guardó el `.amxd`)?
3. ¿La consola de Max muestra la carga del script sin errores inmediatamente al
   confirmar el `node.script`, antes de mandar cualquier mensaje?
4. Si hay generación de contenido (como C&R Generator): ¿se verificó con
   `get_clip_notes` lo que realmente quedó en el clip, no solo el mensaje de
   confirmación de la tool?

## 5. Troubleshooting consolidado

| Síntoma | Causa | Fix |
|---|---|---|
| `node.script: argument must be a <path>` | Falta la ruta al script o `@autostart 1` | Ruta completa + `@autostart 1` |
| Silencio total, device no responde | `@autostart 1` ausente | Agregarlo al objeto `node.script` |
| "No such object" en consola | Typo en nombre de objeto (ej. `coment`) | Corregir el nombre |
| Solo visible abriendo el editor de Max | Objetos sin `presentation: 1` | Activar Presentación + `presentation_rect` en cada objeto del Device View |
| Texto garabateado / letras faltantes | `comment` clásico en vez de `live.comment`, o anchos `patching_rect`/`presentation_rect` distintos | Usar `live.comment`, igualar anchos |
| Etiquetas encimadas en un dial | Franja de nombre+valor de `live.dial` no contada en el alto de fila | Margen extra después de filas con `live.dial` |
| Control se ve bien pero no automatiza / `live.menu` sin opciones | Rango puesto en atributos de nivel superior, no en `saved_attribute_attributes.valueof` | Usar `parameter_mmin`/`parameter_mmax`/`parameter_enum` dentro de `valueof` |
| Device no responde o tarda 30+ seg | Bridge sin `--append-system-prompt`/`--disallowedTools` → el modelo explora el repo | Confirmar esos dos flags en `bridge-persistent.js` |
| "Esta sesión no tiene las tools de Ableton" | Proceso `server.py` huérfano con el puerto OSC ocupado | `pkill` manual + reinsertar el device |
| Un cambio en el `.amxd` "no se nota" en Live | Live no recarga en caliente un device ya insertado | Quitar y volver a arrastrar el device al track |
| Objeto de interfaz vacío con etiqueta `(v8ui)` | El device usa `v8ui`, que requiere Max 9 — este equipo tiene Max 8.6 embebido en Live 12 Suite | No hay workaround: reconstruir sin `v8ui` (ver `max-device/`) o actualizar Max (riesgo de crash ya evaluado y descartado por Brian) |

## 6. Pendiente real (no asumir resuelto)

- Confirmar de punta a punta que `C&R Generator (rebuild)` genera notas reales al
  disparar `New Pair`/`Write Clip` (con `get_clip_notes`, no con el mensaje de
  confirmación).
- DT1 (GIF de demo) sigue sin grabar — requiere a Brian grabando su pantalla.
