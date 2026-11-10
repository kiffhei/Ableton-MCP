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
