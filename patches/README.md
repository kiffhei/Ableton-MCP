# Patches sobre repositorios ajenos

Esta carpeta guarda personalizaciones sobre software de terceros que ableton-mcp
necesita, cuando ese software no vive dentro de este repo y no está respaldado en
ningún lado propio. Ver la regla en `~/proyectos/ba-automation-forge/rules/project-scaffolding.md`
→ "Registro de seguridad".

## abletonosc-browser-user-library.patch

**Qué agrega:** el Remote Script extendido de AbletonOSC instalado en
`~/Music/Ableton/User Library/Remote Scripts/AbletonOSC/abletonosc/track.py` recorre
categorías fijas del Browser de Live (`instruments`, `plugins`, `audio_effects`,
`midi_effects`, `sounds`, `drums`) en sus handlers `/live/browser/scan`,
`/live/browser/get/children`, `/live/browser/load` y `/live/track/load_device` — pero
**nunca incluía `browser.user_library`**. Cualquier `.amxd`/`.adg`/`.ablx` colocado a
mano en `User Library/Presets/...` (el flujo que documenta cada README en `tools/`) era
invisible para `scan_plugins`/`load_plugin` del MCP, sin importar cuántas veces se
reiniciara Ableton — no era un problema de indexado, era que el código nunca miraba esa
categoría del Browser.

Descubierto y confirmado 2026-09-13 probando el flujo end-to-end de Call & Response
Generator: se colocó el `.amxd` en User Library, se reinició Ableton por completo, y
`scan_plugins` seguía sin encontrarlo. La pista fue que `track_load_sample` sí
incluye `browser.user_library` (con `hasattr` de por medio) pero la ruta de carga de
*devices* no.

**Cómo reaplicarlo** (si se reinstala o actualiza AbletonOSC y se pierde la extensión
custom):

```bash
cd "$HOME/Music/Ableton/User Library/Remote Scripts/AbletonOSC"
patch -p1 < ~/proyectos/ableton-mcp/patches/abletonosc-browser-user-library.patch
```

Reiniciar Ableton Live después — los Remote Scripts se cargan una sola vez al arrancar.

**Cómo regenerar el patch** si se vuelve a tocar `track.py`:

```bash
diff -u track.py.antes track.py.despues > ~/proyectos/ableton-mcp/patches/abletonosc-browser-user-library.patch
```

(ajustar las cabeceras `--- a/...` / `+++ b/...` a mano si `diff` las genera con rutas
absolutas — el patch en este repo usa rutas relativas `a/abletonosc/track.py` para que
`patch -p1` funcione parado en la raíz de `AbletonOSC/`).

## abletonosc-load-sample-fix.patch

**Qué agrega:** `track_load_sample` (handler de `/live/track/load_sample`, el OSC que
dispara `load_sample` del MCP) solo buscaba el archivo por nombre dentro de
`browser.sounds`, `browser.drums`, `browser.samples`, `browser.user_library` — ninguna
cubre una carpeta de librería de terceros (ej. Maschine 2:
`~/Documents/Native Instruments/Maschine 2/Samples/...`). Al no encontrarlo ahí, caía a
un *fallback* que nunca pudo funcionar: `browser.load_item("file://" + encoded)` le pasa
un `str` a `Browser.load_item()`, que exige un objeto `BrowserItem` real — siempre
lanzaba `Python argument types ... did not match C++ signature`, capturado y solo
logueado como warning. El MCP nunca se entera: `load_sample` en `src/device_tools.py`
es fire-and-forget y responde "✅ enviado" sin leer la respuesta de Ableton.

Descubierto y confirmado 2026-10-26 construyendo el beat de jungle ragga: 8 samples del
EP-40 "cargaron" según el MCP, ninguno sonó, y el log de AbletonOSC
(`logs/abletonosc.log`) mostró las 8 fallando con ese mismo error de signature.

**Qué cambia el patch:**
1. Agrega `browser.user_folders` (las carpetas marcadas como "Place" en Preferencias >
   Library de Live) a la lista de categorías donde buscar — es el único lugar del
   Browser donde aparecería una carpeta de terceros como la de Maschine, **si esa
   carpeta ya está agregada como Place**. Si no está agregada, hay que agregarla a mano
   en Ableton primero (Preferencias > Library > Places → Add Folder).
2. Quita el fallback roto (nunca pudo funcionar, ver arriba) y en su lugar, si no
   encuentra el archivo en ninguna categoría, loguea `dir(browser)` completo y marca
   cuáles de esos atributos "parecen carpeta" (tienen `.children` o son una colección de
   items con `.children`). Esto es deliberado: `user_folders` es el nombre documentado
   por la comunidad para esa función de la API de Live, pero no hay stubs `.pyi` de Live
   instalados en este Mac ni Remote Scripts oficiales de Ableton que lo usen para
   confirmarlo con certeza. Si `user_folders` no es el atributo correcto (o no existe en
   esta versión de Live), el log de la siguiente carga fallida va a decir exactamente
   qué SÍ expone `browser` — evidencia real en vez de otra adivinanza.

**Verificado en caliente 2026-10-26 13:39** (tras reiniciar Ableton): `browser.user_folders`
era el atributo correcto. Se cargaron 8 samples reales del EP-40 en distintos tracks,
cada uno confirmado contra `abletonosc.log` (`load_sample: loaded '<archivo>' on
'<track>'`), no contra el mensaje fire-and-forget del MCP. Importante: el archivo debe
estar dentro de una carpeta que Ableton reconozca como "Place" (ver Library.cfg o el
panel Places del Browser) — una carpeta del disco que simplemente contiene el archivo,
pero no está registrada como Place, sigue sin encontrarse aunque el patch esté bien.

**Cómo reaplicarlo:**

```bash
cd "$HOME/Music/Ableton/User Library/Remote Scripts/AbletonOSC"
patch -p1 < ~/proyectos/ableton-mcp/patches/abletonosc-load-sample-fix.patch
```

Reiniciar Ableton Live después.

## abletonosc-device-sidechain-routing.patch

**Qué agrega:** seis handlers sobre `abletonosc/device.py` para el ruteo de sidechain
(entrada de audio) de un dispositivo:

```
/live/device/get/available_input_routing_types     /live/device/get/input_routing_type
/live/device/get/available_input_routing_channels  /live/device/set/input_routing_type
                                                   /live/device/get/input_routing_channel
                                                   /live/device/set/input_routing_channel
```

**Por qué:** la API de Live expone `Live.CompressorDevice.CompressorDevice` con
`available_input_routing_types`, `available_input_routing_channels`,
`input_routing_type` e `input_routing_channel` desde Live 11, espejando la API de
routing de pistas — pero AbletonOSC nunca los expuso, ni la copia local ni upstream
(verificado contra `ideoforms/AbletonOSC` el 2026-11-24). Sin esto, montar un sidechain
obliga a abrir el dispositivo y elegir "Audio From" a mano, que es justo lo que se topó
al armar los 13 loops de melodic techno (ver `AUDIT.md`, 2026-11-24).

**Límite real, no supuesto:** **solo el Compressor nativo** tiene esa clase. El Glue
Compressor y el Gate no, aunque su parámetro `S/C On` sí sea un `DeviceParameter`
normal. Por eso cada handler comprueba `hasattr(device, "available_input_routing_types")`
y devuelve `"unsupported"` en vez de reventar. Que el Gate la tenga en alguna versión
está sin confirmar.

**Cómo regenerarlo** desde la copia instalada:

```bash
OSC="$HOME/Music/Ableton/User Library/Remote Scripts/AbletonOSC/abletonosc"
diff -u "$OSC/device.py.orig" "$OSC/device.py" > patches/abletonosc-device-sidechain-routing.patch
```

## abletonosc-delete-device-and-browser-order.patch

**Qué agrega:** dos cosas sobre `abletonosc/track.py`.

1. **`/live/track/delete_device`** — `track.delete_device(index)` existe en la API de
   Live, y AbletonOSC exponía `delete_clip` y `delete_track` pero no este. Sin él, un
   dispositivo cargado por error no se puede quitar sin ratón; lo único posible era
   dejarlo en bypass. Valida el índice contra `len(track.devices)` antes de borrar.

2. **Orden y criterio de búsqueda de `load_device`.** El buscador devolvía el *primer*
   item cuyo nombre *contuviera* la consulta, recorriendo `browser.plugins` **antes**
   que `browser.audio_effects`. Pedir `"Compressor"` cargaba el Audio Unit
   `AUMultibandCompressor` en vez del Compressor de Live. El parche hace dos cambios:
   los nativos se recorren primero, y entre todas las coincidencias gana el **nombre
   exacto**; si no hay, el **más corto**. Ambos criterios eligen el dispositivo simple
   frente al plugin de nombre largo que lo contiene.

**Cómo regenerarlo:** igual que el anterior, con `track.py`.

---

## Recargar el Remote Script después de aplicar un parche

Los cambios **no** se cargan solos, y AbletonOSC no expone ninguna recarga por OSC.

> **No reinicies Live si tienes trabajo sin guardar.** En
> *Preferences → Link/Tempo/MIDI*, pon el Control Surface de AbletonOSC en `None` y
> vuelve a elegir `AbletonOSC`. Eso recarga el script conservando la sesión.

Para comprobar que cargó, un handler nuevo debe dejar de responder `None`:

```bash
# devuelve "unsupported" en un device sin sidechain, un nombre de pista si lo tiene
/live/device/get/input_routing_type <track> <device>
```

## abletonosc-ableton-mcp-completo.patch  ← usar este para reinstalar

**Qué es:** todos nuestros cambios sobre AbletonOSC en un solo parche, generado contra
**upstream limpio** (`ideoforms/AbletonOSC`, rama `master`).

**Por qué existe.** Los cuatro parches individuales de arriba se generaron cada uno
contra el estado local del momento, así que **dependen del orden y no aplican sobre
upstream**. Comprobado el 2026-11-24 con `git apply --check` sobre un clon limpio: solo
el de sidechain pasa; los tres de `track.py` fallan. Sirven para documentar *por qué*
existe cada cambio; para **reinstalar**, usar este.

**Verificado:** aplica limpio sobre upstream y deja `device.py` y `track.py` idénticos
byte a byte a la copia instalada.

```bash
git clone https://github.com/ideoforms/AbletonOSC.git
cd AbletonOSC && git apply ~/proyectos/ableton-mcp/patches/abletonosc-ableton-mcp-completo.patch
```

**Para regenerarlo** (hay un clon de upstream en `~/proyectos/_referencias-ableton/AbletonOSC`):

```bash
OSC="$HOME/Music/Ableton/User Library/Remote Scripts/AbletonOSC/abletonosc"
REF="$HOME/proyectos/_referencias-ableton/AbletonOSC"
cd "$REF" && git checkout -- abletonosc/
for m in device track; do diff -u "$REF/abletonosc/$m.py" "$OSC/$m.py"; done \
  > ~/proyectos/ableton-mcp/patches/abletonosc-ableton-mcp-completo.patch
```
