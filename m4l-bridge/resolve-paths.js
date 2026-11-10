// Resolución de rutas para los bridges de Max for Live.
//
// Por qué existe este archivo: Max for Live, lanzado desde Finder o el Dock, NO
// hereda el $PATH ni las variables de un shell interactivo (ver DEV9 en
// ../DEV_TASKS.md). Eso descarta dos soluciones que parecen obvias:
//
//   - `spawn("claude", ...)` a secas          → ENOENT dentro de Max
//   - `process.env.ALGO` como único mecanismo → undefined dentro de Max
//
// Y hardcodear una ruta absoluta metería `/Users/<alguien>/...` en un repo
// público (VIT2). Así que se resuelve sin depender del entorno:
//
//   - REPO_PATH: derivado de la ubicación de este archivo. El bridge vive en
//     <repo>/m4l-bridge/, así que la raíz del repo es el directorio padre.
//     No requiere configuración y es correcto en cualquier máquina.
//   - CLAUDE_BIN: variable de entorno si está definida (gana siempre, para
//     instalaciones fuera de lo común), y si no, se sondean las ubicaciones
//     reales donde el instalador de Claude Code deja el binario.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const REPO_PATH = path.dirname(__dirname);
const SERVER_PY_PATH = path.join(REPO_PATH, "src", "server.py");

// Ubicaciones habituales del binario, en orden de probabilidad. No se leen del
// $PATH a propósito: dentro de Max ese $PATH no es el del shell del usuario.
const CANDIDATOS_CLAUDE = [
  path.join(os.homedir(), ".local", "bin", "claude"),
  path.join(os.homedir(), ".claude", "local", "claude"),
  path.join(os.homedir(), ".bun", "bin", "claude"),
  "/opt/homebrew/bin/claude",
  "/usr/local/bin/claude",
  "/usr/bin/claude",
];

const esEjecutable = (ruta) => {
  try {
    fs.accessSync(ruta, fs.constants.X_OK);
    return fs.statSync(ruta).isFile();
  } catch {
    return false;
  }
};

// Último recurso: sirve cuando el script se corre desde una terminal (los
// test-*.js), no cuando lo lanza Max. Por eso va al final, no al principio.
const buscarEnPath = () => {
  try {
    const ruta = execFileSync("which", ["claude"], { encoding: "utf8" }).trim();
    return esEjecutable(ruta) ? ruta : null;
  } catch {
    return null;
  }
};

const resolverClaudeBin = () => {
  const declarado = process.env.ABLETON_MCP_CLAUDE_BIN;
  if (declarado) {
    if (esEjecutable(declarado)) return declarado;
    throw new Error(
      `ABLETON_MCP_CLAUDE_BIN apunta a "${declarado}", que no es un ejecutable. ` +
        `Corrígelo con la salida de \`which claude\`.`
    );
  }

  const encontrado = CANDIDATOS_CLAUDE.find(esEjecutable) || buscarEnPath();
  if (encontrado) return encontrado;

  throw new Error(
    "No se encontró el binario `claude`. Se buscó en:\n" +
      CANDIDATOS_CLAUDE.map((c) => `  - ${c}`).join("\n") +
      "\nExporta la ruta explícitamente:\n" +
      "  export ABLETON_MCP_CLAUDE_BIN=\"$(which claude)\"\n" +
      "Ver m4l-bridge/README.md."
  );
};

module.exports = { REPO_PATH, SERVER_PY_PATH, resolverClaudeBin };
