# m4l-bridge — Bridge Node for Max

Conecta un device de Max for Live con Claude Code, que a su vez habla con el
MCP server "ableton" (`../src/server.py`) para controlar Ableton Live.

---

## Qué archivo usar

| Archivo | Cuándo |
|---|---|
| `bridge-simple.js` | Un proceso `claude` nuevo por cada mensaje. Sirve para validar el flujo end-to-end (ver DEV10 en `../DEV_TASKS.md`). Más lento: paga el arranque de `claude` en cada llamada. |
| `bridge-persistent.js` | Un solo proceso `claude` corriendo toda la sesión (stream-json). Uso en vivo — el que carga el patch `Claude Channel Strip.amxd`. |
| `test-bridge.js` | Prueba de humo de `bridge-simple.js` desde terminal, sin Max. |
| `test-persistent.js` | Prueba de humo de `bridge-persistent.js` desde terminal, sin Max — manda dos turnos seguidos para validar `--resume`/streaming. |

---

## Configuración — normalmente ninguna

Las rutas las resuelve `resolve-paths.js` sin depender del entorno, porque
**Max for Live, lanzado desde Finder o el Dock, no hereda el `$PATH` ni las
variables de un shell interactivo** (ver DEV9 en `../DEV_TASKS.md`). Eso
descarta las dos soluciones que parecen obvias: `spawn("claude", ...)` a secas
da `ENOENT` dentro de Max, y una variable de entorno como único mecanismo llega
`undefined`. Y hardcodear la ruta absoluta metería `/Users/<alguien>/...` en un
repo público.

| Ruta | Cómo se resuelve |
|---|---|
| Raíz del repo | Derivada de la ubicación del propio archivo — el bridge vive en `<repo>/m4l-bridge/`, así que la raíz es el directorio padre. Correcto en cualquier máquina, sin configurar nada. |
| Binario `claude` | Se sondean las ubicaciones donde el instalador de Claude Code deja el binario (`~/.local/bin`, `~/.claude/local`, `~/.bun/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`). Como último recurso, `which claude` — que sirve al correr desde terminal, no desde Max. |

### Cuándo sí hace falta configurar

Sólo si tu `claude` está instalado fuera de esas ubicaciones. La variable gana
siempre sobre el sondeo:

```bash
export ABLETON_MCP_CLAUDE_BIN="$(which claude)"
```

Si no se encuentra el binario, el script falla de inmediato con la lista de
rutas que buscó y el comando exacto para resolverlo — no arranca a medias ni
apunta en silencio a la máquina de otra persona.

---

## Instalación

```bash
cd m4l-bridge
npm install
```

`max-api` viene incluido con la instalación de Max — la entrada en
`package.json` es solo para que el editor no marque el `require` como error.
