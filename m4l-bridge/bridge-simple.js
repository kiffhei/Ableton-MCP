const { spawn } = require("child_process");
const Max = require("max-api");

let sessionId = null;
const CLAUDE_BIN = "/Users/brianear/.local/bin/claude";
const REPO_PATH = "/Users/brianear/proyectos/ableton-mcp";

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
