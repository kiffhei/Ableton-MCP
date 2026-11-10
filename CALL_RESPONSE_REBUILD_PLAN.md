# Plan — Rebuild de Call & Response Generator para Max 8.6

> Contexto completo en AUDIT.md Addendum 7 y 8. Este archivo es el plan de construcción,
> no el registro de lo ya hecho.

## Por qué existe esto

El device de Side Brain (`tools/call-response-generator/`) usa un objeto `v8ui`
(JS sobre V8) que no existe en Max 8.6 — el Max embebido en el Ableton Live 12 Suite de
Brian. Confirmado en vivo: el device no genera nada, ni visual ni musicalmente. Brian
decidió no actualizar Ableton ni instalar Max 9 standalone (riesgo de crash conocido).

El motor generativo real es open source: **github.com/Nordl3/Call-Response-Generator**
(MIT), una web app de un solo archivo (`index.html`, ~1730 líneas, JS moderno sin
ofuscar). Las "extensiones" que Side Brain agregó sobre ese motor (swing, gate feel,
slide/accent profiles, 8 presets, undo de 24 pasos) **no son públicas** — solo existen
en su `.amxd` empacado en un formato binario (`mx@c`) que no es el mismo JSON plano
reverse-engineered en AUDIT.md Addendum 4 para otro device. No se intenta abrir ese
paquete — se reconstruye el motor de Nordl3 desde su fuente real.

Mapa visual de referencia (se actualiza conforme avanza la construcción):
https://claude.ai/code/artifact/24eafad6-38a9-4cae-9d03-b4cd2c0b65ee

## Alcance v1 (12 controles)

| Control | Tipo Max | Fuente de datos |
|---|---|---|
| Style | live.menu | `stylePresetMap()` — 46 entradas (solo datos, no lógica por estilo) |
| Key | live.menu | 12 notas |
| Scale | live.menu | `SCALE_INTERVALS` — 41 escalas |
| Response Strategy | live.menu | `responseStrategies` — 38 entradas |
| Motif Type | live.menu | `motifTypes` — 28 entradas |
| Ending Behaviour | live.menu | `endingBehaviours` — 13 entradas |
| Octave | live.dial (knob) | C1–C5 |
| Steps | live.dial (knob) | 2–16 |
| Density | live.dial (knob) | 0.0–1.0 |
| Note Length | live.slider (fader) | 40%–200%, del original |
| Seed | live.numbox | agregado propio — el original usaba `Math.random()` sin seed |
| New Pair | live.button | dispara `motifTemplate()` + `responseStrategy` |
| Mutate | live.button | dispara `mutatePhrase()` |
| Write Clip | live.button | escribe call+response al clip vía OSC |

Fuera de v1 (se agregan después si el motor base funciona): swing/gate/slide/accent
profiles, 8 presets recallables, undo de 24 pasos, phrase modes de doble lane
simultánea, sonido de previsualización (no aplica — Ableton ya reproduce el clip).

## Pasos de construcción

1. **Portar el motor JS de Nordl3 a JS compatible con el objeto `js` de Max 8.6**
   (no `v8ui`/`v8` — esos no existen en 8.6). Adaptar de ES6 moderno a sintaxis segura
   para el engine legado de Max (evitar arrow functions/let/const si el engine de la
   versión instalada no las soporta — confirmar leyendo la documentación del objeto
   `js` para Max 8, o degradar a ES5 directamente para no depender de eso). Reemplazar
   `Math.random()` por un PRNG con seed (reusar el mismo patrón mulberry32 que ya usa
   `progression_generator.py` en este proyecto, para consistencia).
   Copiar tablas de datos (`stylePresetMap`, `SCALE_INTERVALS`, listas de estrategias/
   motifs/endings) tal cual — son datos, no lógica, bajo riesgo.

2. **Construir el patcher como JSON plano**, no como el binario `mx@c` de Side Brain.
   Definir los boxes necesarios: `live.menu` ×6, `live.dial` ×3, `live.slider` ×1,
   `live.numbox` ×1, `live.button` ×3, un objeto `js` cargando el archivo portado,
   `thispatcher` para atributos de presentación, y el wrapper estándar de MIDI Effect
   (sin `notein`/`noteout` de audio — este device no filtra MIDI entrante, genera y
   escribe directo a un clip vía LiveAPI desde el propio `js`). Cada UI object necesita
   `varname` + `parameter_visible` correcto para que Live lo exponga como parámetro
   automatizable (confirmable después con `get_device_params`, no antes).

3. **Empaquetar como `.amxd`**: mismos 3 chunks `ampf`+`meta`+`ptch` (tag(4)+len_le(4)+
   payload) documentados en AUDIT.md Addendum 4, con `ptch` = el patcher JSON en texto
   plano (no re-comprimido ni re-encodeado en el formato `mx@c`).

4. **Cargar en Ableton**: copiar a
   `User Library/Presets/MIDI Effects/Max MIDI Effect/`, `scan_plugins(filter=...)`
   para confirmar que aparece (el patch de `browser.user_library` de Addendum 7 ya
   resuelve esto), `load_plugin` para cargarlo en un track de prueba.

5. **Verificar sin depender de la vista de Brian**:
   `get_track_devices` (¿cargó?) → `get_device_params` (¿aparecen los 12 controles con
   los nombres esperados?) → `set_device_param` (operar cada uno) → armar track, grabar
   un clip, disparar New Pair + Write Clip → `get_clip_notes` (¿salieron notas reales,
   coherentes con Style/Key/Scale configurados?).
   Solo si algo falla silenciosamente (carga pero no genera, o no carga en absoluto) se
   le pide a Brian el texto exacto de la Consola de Max — no antes.

## Riesgos conocidos

- No hay forma de abrir el editor de Max para verificar visualmente el patcher armado
  a mano — el ciclo de verificación del paso 5 es la única señal hasta que Brian lo
  vea. Si `get_track_devices` muestra 0 devices tras cargar, lo más probable es un
  patcher JSON inválido — revisar estructura antes de asumir un problema de Ableton.
- El objeto `js` legado de Max tiene un motor JS más limitado que V8 — si algo de la
  sintaxis portada no corre, probablemente falle en silencio (sin señal por OSC) hasta
  que se pruebe generar y `get_clip_notes` devuelva vacío.
- Sin acceso al código de las extensiones de Side Brain, el resultado será fiel al
  motor de Nordl3, no una réplica exacta del device comercial.

## Estado (actualizado 2026-09-14 01:05, corrida automática nocturna vía CronCreate)

- [x] Motor JS portado y validado en Python/Node de forma aislada (sin Max todavía)
      — `max-device/cr_engine.js`, ES5 estricto (sin let/const/arrow/spread/??/?.).
      Validado con `max-device/test_engine.js`: determinismo con seed, MIDI válido,
      **las 46×38=1748 combinaciones de estilo×estrategia corren sin excepción**.
      Licencia MIT de Nordl3 copiada en `max-device/cr_engine.LICENSE`.
- [x] Glue del objeto `js` escrito — `max-device/cr_device.js` (v0: New Pair, Mutate,
      Write Clip, cfg fijo — los setters de Style/Key/Scale/etc. ya están pero sin
      controles del patcher todavía conectados). Investigado y documentado el
      mecanismo real de LiveAPI para escribir en un clip (fuente:
      adammurray.link/max-for-live/js-in-live/, no adivinado) — ver "Hallazgos" abajo.
- [ ] Patcher JSON construido — **siguiente paso pendiente**, no iniciado esta noche
      (se decidió no construirlo a las 1am sin poder probarlo con calma; lo demás
      del pipeline ya está listo para cuando se retome)
- [ ] Empaquetado como `.amxd`
- [ ] Cargado en Ableton (`get_track_devices` confirma)
- [ ] Parámetros reconocidos por Live (`get_device_params` confirma los 12 controles)
- [ ] Generación verificada con notas reales (`get_clip_notes` tras New Pair + Write Clip)
- [ ] Mapa visual (artifact) actualizado con el estado real, no "planeado" en todo

### Hallazgos de la corrida nocturna (Live API — antes de esto no estaban confirmados)

Fuente: adammurray.link/max-for-live/js-in-live/live-api/ y .../generating-midi-clips/
(tutorial específico del objeto `js` legado, no de v8 — exactamente lo que aplica aquí).

1. **`new LiveAPI(...)` nunca debe llamarse en código de nivel superior** — falla en
   silencio durante la inicialización del device (sin error visible en el flujo OSC).
   `cr_device.js` ya respeta esto: todo `new LiveAPI(...)` vive dentro de una función
   disparada por mensaje (`writeclip()`), nunca a nivel de módulo.
2. **Bug conocido del engine:** `if (!clipSlot.get("has_clip"))` siempre da `false`
   negado — hay que escribir `if (clipSlot.get("has_clip") == false)` explícito.
3. **El track del device se obtiene con `new LiveAPI("this_device canonical_parent")`**
   — no hace falta (ni conviene) hardcodear un índice de track. `cr_device.js` ya usa
   este patrón.
4. **`add_new_notes` necesita `{notes: notes}` explícito**, no el shorthand `{notes}`
   (ES6, no existe en el motor ES5 de Max) — ya aplicado.
5. Escribir un clip requiere: `clipSlot.call("create_clip", length)` si
   `has_clip==false`, luego `clip.call("remove_notes_extended", 0, 128, 0, clip.get("length"))`
   para limpiar, luego `clip.call("add_new_notes", {notes: [...]})`.

### Por qué se detuvo aquí (no se construyó el patcher JSON todavía)

Construir el patcher (`live.menu`×6, `live.dial`×3, `live.slider`×1, `live.numbox`×1,
`live.button`×3, el objeto `js`, `thispatcher`, wrapper de MIDI Effect) a mano como
JSON es la parte más nueva y riesgosa del plan — nunca se ha armado un patcher de Max
completo desde cero en este proyecto (solo se editaron devices ya existentes, ver
AUDIT.md Addendum 4). Con Ableton abierto y sin nadie despierto para revisar un error
de la Consola de Max si algo sale mal, se priorizó dejar el terreno más firme posible
(motor validado + mecanismo de escritura investigado con fuente real, no adivinado)
en vez de arriesgar un intento apurado a la 1am. Retomar directo desde aquí: construir
el patcher JSON (Paso 2 del plan de arriba), empaquetarlo (Paso 3), cargarlo y
verificar (Pasos 4-5).
