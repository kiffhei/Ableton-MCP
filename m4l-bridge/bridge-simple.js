const { spawn } = require("child_process");
const Max = require("max-api");

let sessionId = null;
// Rutas resueltas sin depender del $PATH ni del entorno del shell — Max no los
// hereda. Ver resolve-paths.js y DEV9 en ../DEV_TASKS.md.
const { REPO_PATH, resolverClaudeBin } = require("./resolve-paths");

const CLAUDE_BIN = resolverClaudeBin();

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
