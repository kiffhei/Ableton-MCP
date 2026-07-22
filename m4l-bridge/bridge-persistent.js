const { spawn, execSync } = require("child_process");
const readline = require("readline");
const Max = require("max-api");

const CLAUDE_BIN = "/Users/brianear/.local/bin/claude";
const REPO_PATH = "/Users/brianear/proyectos/ableton-mcp";
const SERVER_PY_PATH = `${REPO_PATH}/src/server.py`;

// Node for Max no siempre mata el proceso node.script anterior cuando el
// device se saca/reinserta (confirmado: quedaban dos cadenas Max→node→claude→
// server.py corriendo en paralelo). La vieja se queda con el puerto OSC 11001
// tomado, y la nueva sesión de claude nunca logra conectar su propio MCP
// "ableton" — se queda sin las tools sin ningún error visible. Por eso cada
// carga mata primero cualquier server.py huérfano de una sesión anterior,
// antes de arrancar la propia.
try {
  execSync(`pkill -f "${SERVER_PY_PATH}"`);
  Max.post("bridge-persistent: server.py huérfano encontrado y terminado");
  execSync("sleep 0.5"); // darle tiempo al SO a liberar el puerto UDP
} catch (e) {
  // pkill sale con código != 0 si no había nada que matar — no es un error
}

// Sin system prompt ni restricción real de tools, este proceso heredaba TODO
// el entorno personal del usuario (reglas globales de CLAUDE.md, hooks, decenas
// de tools no relacionadas) y para una instrucción simple terminaba explorando
// el repo (ej: leyendo track_tools.py) en vez de llamar la tool directamente —
// eso es lo que se percibía como "se queda pasmado". --allowedTools solo
// pre-aprueba, no bloquea el resto: hace falta --disallowedTools explícito
// para las tools genéricas, más un system prompt que fuerce acción directa.
const DISALLOWED_TOOLS = [
  "Agent", "Artifact", "Bash", "CronCreate", "CronDelete", "CronList",
  "DesignSync", "EnterWorktree", "ExitWorktree", "Edit", "Monitor",
  "NotebookEdit", "PushNotification", "Read", "Grep", "Glob", "RemoteTrigger",
  "ScheduleWakeup", "SendMessage", "Skill", "TaskCreate", "TaskGet",
  "TaskList", "TaskOutput", "TaskStop", "TaskUpdate", "ToolSearch",
  "WebFetch", "WebSearch", "Write", "ReportFindings",
].join(",");

const SYSTEM_PROMPT =
  "Sos un controlador de Ableton Live vía MCP, nada más. Para cada mensaje " +
  "del usuario: interpretalo y llamá DIRECTAMENTE la tool mcp__ableton__ que " +
  "corresponda con los argumentos correctos. No leas archivos del repo, no " +
  "explores el código, no apliques metodologías de desarrollo (sin TDD, sin " +
  "planificar, sin revisar código) — tu única tarea en esta sesión es " +
  "traducir la instrucción en lenguaje natural a la llamada de tool correcta " +
  "y responder con un resumen breve de una línea del resultado.";

const claude = spawn(CLAUDE_BIN, [
  "-p", "--input-format", "stream-json", "--output-format", "stream-json",
  "--verbose",
  "--allowedTools", "mcp__ableton__*",
  "--disallowedTools", DISALLOWED_TOOLS,
  "--append-system-prompt", SYSTEM_PROMPT,
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
