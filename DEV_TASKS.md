# DEV_TASKS.md — Ableton Live MCP Server | Tareas de código
> Para sesión dedicada de Claude Code. Fecha: 2026-06-17.

---

## Contexto

MCP server en Python que conecta Claude con Ableton Live via AbletonOSC.
Ruta local: `~/proyectos/ableton-mcp/`
Stack: Python 3.10+ · mcp · python-osc
Archivo principal: `src/server.py` (1275 líneas, 19 tools)
Estado: funcional como herramienta, sin git, sin GitHub.

---

## DEV1 · Crear `.gitignore` `[XS]` — HACER PRIMERO

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyc
*.so
.env
venv/
.venv/
*.egg-info/

# Proyectos musicales (datos de producción personales)
projects/

# Claude Code interno
.claude/

# macOS
.DS_Store
*.DS_Store

# Editores
.vscode/
.idea/
```

**IMPORTANTE:** crear este archivo ANTES de `git init`.

---

## DEV2 · Inicializar git y publicar en GitHub `[S]`

```bash
cd ~/proyectos/ableton-mcp

# Verificar que .gitignore existe y projects/ no será commiteado
cat .gitignore | grep "projects"

# Inicializar
git init
git add .
git status  # verificar que projects/ NO aparece en staged

# Primer commit
git commit -m "feat: Ableton Live MCP server — 19 tools, music theory engine"

# Crear repo público en GitHub
gh repo create kiffhei/ableton-mcp --public --push --source=.
```

---

## DEV3 · Actualizar README — capacidades reales `[S]`

Archivo: `README.md`

**Cambios específicos:**

1. Agregar elevator pitch después del título:
   ```md
   > Controla Ableton Live con lenguaje natural via Claude Code.
   > Motor de teoría musical para progresiones en cualquier tonalidad/escala,
   > estado persistente de proyectos, y clonado de canciones reales vía Spotify.
   > Construido con el Model Context Protocol (MCP) de Anthropic.
   ```

2. Expandir tabla de herramientas (7 → 19):
   ```md
   | Herramienta | Descripción |
   |---|---|
   | `add_chord_progression` | Genera progresiones en cualquier tonalidad y escala |
   | `add_midi_notes` | Agrega notas MIDI individuales con control total |
   | `create_midi_track` | Crea un nuevo track MIDI con nombre y color |
   | `set_tempo` | Cambia el BPM del proyecto |
   | `play_pause` | Controla reproducción |
   | `get_session_info` | Info del proyecto: tracks, escenas, BPM |
   | `set_clip_color` | Colorea clips por índice RGB |
   | `load_instrument` | Carga un instrumento nativo de Ableton |
   | `load_plugin` | Carga un plugin VST/AU instalado |
   | `load_sample` | Carga un archivo WAV en un Simpler |
   | `get_device_params` | Lee los parámetros de un device/plugin |
   | `set_device_param` | Modifica un parámetro específico |
   | `set_device_params_bulk` | Modifica múltiples parámetros en una llamada |
   | `get_track_devices` | Lista los devices de un track |
   | `scan_plugins` | Escanea plugins instalados por nombre |
   | `new_project` | Crea un nuevo proyecto con estado persistente |
   | `load_project` | Carga el estado de un proyecto guardado |
   | `save_project_state` | Guarda el estado actual del proyecto |
   | `list_projects` | Lista todos los proyectos guardados |
   ```

3. Actualizar sección de estilos:
   ```md
   ### Géneros soportados

   60+ géneros con progresiones características predefinidas:
   house, deep_house, tech_house, afro_house, techno, minimal_techno,
   hip_hop, lo_fi, trap, drill, boom_bap, rnb, neo_soul, jazz, jazz_fusion,
   drum_and_bass, ambient, synthwave, afrobeats, amapiano, reggaeton, y más.

   Para cualquier estilo o combinación usa raíz + escala directamente:
   cualquier nota (C, F#, Bb...) × cualquier escala (mayor, menor, dórica,
   frigia, pentatónica, blues, doble armónica...).
   ```

4. Agregar sección "Arquitectura" con diagrama ASCII (ver DESIGN_TASKS.md DT2).

---

## DEV4 · Limpiar CLAUDE.md para repo público `[S]`

Decidir entre las dos opciones:

**Opción A (recomendada):** Mover CLAUDE.md actual a `CLAUDE.internal.md`:
```bash
mv CLAUDE.md CLAUDE.internal.md
echo "CLAUDE.internal.md" >> .gitignore
```
Crear `CLAUDE.md` público con solo la información técnica del MCP (sin rutas personales, sin sesión activa, sin equipamiento personal).

**Opción B:** Limpiar el CLAUDE.md existente:
- Remover toda la sección "Sesión activa"
- Remover "Librería de samples del usuario" (o reemplazar rutas con `[TU_RUTA_AQUI]`)
- Remover "Referencia de hardware equivalente" (equipamiento personal)
- Mantener: Flujo de inicio, MCPs disponibles, Sistema de tonalidades, Flujo de clonado, Reglas de comportamiento, Referencia de instrumentos, Efectos por género, Géneros disponibles

---

## DEV5 · Refactor: separar server.py en módulos `[L]`

`server.py` tiene 1275 líneas. Separar en:

```
src/
├── server.py          (~200 líneas: MCP server, list_tools, call_tool)
├── music_theory.py    (~300 líneas: CHROMATIC, SCALES, CHORD_TYPES, GENRE_PATTERNS, helpers)
├── osc_client.py      (~80 líneas: init_osc_client, send_osc, osc_response_handler, start_osc_listener)
└── project_manager.py (~100 líneas: PROJECTS_DIR, _slug, _load_project_file, _save_project_file)
```

Imports en server.py:
```python
from music_theory import build_chord, build_progression, note_name_to_midi, scale_degree_to_root
from osc_client import init_osc_client, send_osc, start_osc_listener
from project_manager import new_project, load_project, save_project
```

**Beneficio para portafolio:** cualquier reclutador que abra el repo ve módulos cohesivos, no un monolito.

---

## DEV6 · Agregar tests de música theory `[M]`

Requiere DEV5 (separar music_theory.py para poder importarlo sin el servidor MCP).

Crear `tests/test_music_theory.py`:
```python
import pytest
import sys
sys.path.insert(0, "src")
from music_theory import note_name_to_midi, scale_degree_to_root, build_chord, build_progression

def test_note_to_midi_c4():
    assert note_name_to_midi("C", 4) == 60

def test_note_to_midi_a4():
    assert note_name_to_midi("A", 4) == 69

def test_scale_c_major():
    from music_theory import SCALES, NOTE_TO_MIDI
    root = NOTE_TO_MIDI["C"]
    scale = [root + i for i in SCALES["major"]]
    assert scale == [60, 62, 64, 65, 67, 69, 71]

def test_build_chord_major():
    notes = build_chord(60, "maj")  # C mayor
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 64, 67]  # C E G

def test_build_chord_minor():
    notes = build_chord(60, "min")  # C menor
    pitches = [n["pitch"] for n in notes]
    assert pitches == [60, 63, 67]  # C Eb G
```

Instalar pytest: agregar `pytest>=8.0` a `requirements.txt`.
Comando: `pytest tests/ -v`

---

## DEV7 · Estructura del bridge Node for Max (`m4l-bridge/`) `[M]`

Crear carpeta nueva en la raíz del repo:

```
m4l-bridge/
├── package.json
├── bridge-simple.js       (un proceso `claude` por mensaje — para validar el flujo)
├── bridge-persistent.js   (un solo proceso `claude` corriendo toda la sesión — para uso en vivo)
└── README.md              (cuál usar y cuándo)
```

`package.json`:
```json
{
  "name": "ableton-mcp-m4l-bridge",
  "version": "0.1.0",
  "private": true,
  "description": "Bridge Node for Max: conecta un device de Max for Live con Claude Code (MCP server 'ableton')",
  "dependencies": {
    "max-api": "*"
  }
}
```
Nota: `max-api` viene incluido con la instalación de Max — esta entrada es solo para que el editor no marque el `require` como error.

`bridge-simple.js`:
```javascript
const { spawn } = require("child_process");
const Max = require("max-api");

let sessionId = null;
const CLAUDE_BIN = "CLAUDE_BIN_PLACEHOLDER"; // ver DEV9 — reemplazar con `which claude`
const REPO_PATH = "/Users/TU_USUARIO/proyectos/ableton-mcp";

Max.addHandler("ask", (trackIndex, ...promptWords) => {
  const args = [
    "-p", promptWords.join(" "),
    "--append-system-prompt",
    `Estás controlando el track ${trackIndex} de Ableton Live vía el MCP server "ableton". Aplica las acciones a ese track_index salvo que el usuario indique otro explícitamente.`,
    "--output-format", "json",
    "--allowedTools", "mcp__ableton__*",
  ];
  if (sessionId) args.push("--resume", sessionId);

  const proc = spawn(CLAUDE_BIN, args, { cwd: REPO_PATH });
  let out = "";
  proc.stdout.on("data", d => out += d);
  proc.stderr.on("data", d => Max.post("stderr: " + d));
  proc.on("close", () => {
    try {
      const parsed = JSON.parse(out);
      sessionId = parsed.session_id;
      Max.outlet("response", parsed.result);
    } catch {
      Max.outlet("error", "respuesta no parseable");
    }
  });
});
```

`bridge-persistent.js`:
```javascript
const { spawn } = require("child_process");
const readline = require("readline");
const Max = require("max-api");

const CLAUDE_BIN = "CLAUDE_BIN_PLACEHOLDER"; // ver DEV9
const REPO_PATH = "/Users/TU_USUARIO/proyectos/ableton-mcp";

const claude = spawn(CLAUDE_BIN, [
  "-p", "--input-format", "stream-json", "--output-format", "stream-json",
  "--verbose", "--allowedTools", "mcp__ableton__*",
], { cwd: REPO_PATH });

readline.createInterface({ input: claude.stdout }).on("line", (line) => {
  try {
    const msg = JSON.parse(line);
    if (msg.type === "result") Max.outlet("response", msg.result);
  } catch {}
});

claude.stderr.on("data", d => Max.post("stderr: " + d));

let currentTrack = null;
Max.addHandler("track", (t) => { currentTrack = t; });
Max.addHandler("ask", (...words) => {
  const text = `[track ${currentTrack}] ${words.join(" ")}`;
  const userMsg = { type: "user", message: { role: "user", content: [{ type: "text", text }] } };
  claude.stdin.write(JSON.stringify(userMsg) + "\n");
});
```

**IMPORTANTE — no confundir con DEV5:** este bridge NO toca `server.py`. Claude Code habla con el MCP server "ableton" vía stdio exactamente igual que en una sesión normal de terminal; el bridge solo lanza el binario `claude`.

---

## DEV8 · Verificar que el MCP server "ableton" responde en modo headless `[XS]` — HACER ANTES DE DEV7

```bash
# Confirmar que el servidor está registrado y Claude Code lo ve
claude mcp list

# Probar exactamente la misma invocación que hará el bridge
cd ~/proyectos/ableton-mcp
claude -p "Lista las herramientas disponibles del servidor ableton" \
  --allowedTools "mcp__ableton__*" \
  --output-format json
```
Verificar en el JSON de salida: `is_error: false` y que `result` menciona tools reales (`add_chord_progression`, `set_tempo`, etc.). Si `claude mcp list` no muestra "ableton" conectado, DETENERSE aquí — nada de lo siguiente funcionará sin esto.

---

## DEV9 · Resolver ruta absoluta del binario `claude` `[XS]`

```bash
which claude
```
Max for Live (lanzado desde Finder/Dock) no hereda el `$PATH` de tu shell — `node.script` con `"claude"` a secas falla con `ENOENT`. Reemplazar `CLAUDE_BIN_PLACEHOLDER` en ambos bridges con la ruta literal que devuelve este comando.

---

## DEV10 · Test E2E del bridge simple desde terminal, sin Max `[S]`

Antes de tocar Max, validar el bridge en aislamiento:

```javascript
// m4l-bridge/test-bridge.js
const { spawn } = require("child_process");
const CLAUDE_BIN = "CLAUDE_BIN_PLACEHOLDER"; // mismo valor que DEV9

const proc = spawn(CLAUDE_BIN, [
  "-p", "Crea una progresión de deep house en Dm en el track 0",
  "--append-system-prompt", "Estás controlando el track 0 de Ableton Live vía el MCP server \"ableton\".",
  "--output-format", "json",
  "--allowedTools", "mcp__ableton__*",
], { cwd: process.cwd() });

let out = "";
proc.stdout.on("data", d => out += d);
proc.on("close", () => console.log(JSON.parse(out)));
```

Correr con Ableton Live abierto y AbletonOSC activo: `node m4l-bridge/test-bridge.js`
**Verificación:** el track 0 debe mostrar el clip con la progresión generada, y la consola debe imprimir JSON con `is_error: false`.

---

## DEV11 · Migrar a `bridge-persistent.js` `[M]` — SOLO si DEV10 pasa

No migrar si el test E2E del bridge simple falla — depurar ahí primero, no en el patch de Max.
Una vez validado: en el patch de Max (ver DESIGN_TASKS.md DT4), el objeto `node.script` debe apuntar a `m4l-bridge/bridge-persistent.js` en vez de `bridge-simple.js`.

---

## Orden de ejecución

1. **DEV1** → 5 min
2. **DEV4** → 15 min (limpiar CLAUDE.md antes del primer commit)
3. **DEV3** → 30 min (actualizar README)
4. **DEV2** → 10 min (git init + GitHub)
5. **DEV5** → 60 min (refactor en módulos — sesión separada)
6. **DEV6** → 30 min (tests — requiere DEV5)

**Sesión independiente — M4L Channel Strip (ver PROMPT_KICKOFF.md KICKOFF C):**

7. **DEV8** → 5 min (verificar MCP headless — hacer primero, bloquea todo lo demás)
8. **DEV9** → 2 min (ruta del binario claude)
9. **DEV7** → 30 min (crear los dos bridges)
10. **DEV10** → 15 min (test E2E sin Max)
11. **DEV11** → 10 min (migrar a persistente, solo si DEV10 pasa)
