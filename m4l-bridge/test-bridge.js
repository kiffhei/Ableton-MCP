// m4l-bridge/test-bridge.js
const { spawn } = require("child_process");
// Configurar via variable de entorno — ver m4l-bridge/README.md
const { resolverClaudeBin } = require("./resolve-paths");

const CLAUDE_BIN = resolverClaudeBin();

const proc = spawn(CLAUDE_BIN, [
  "-p", "Crea una progresión de deep house en Dm en el track 0",
  "--append-system-prompt", "Estás controlando el track 0 de Ableton Live vía el MCP server \"ableton\".",
  "--output-format", "json",
  "--allowedTools", "mcp__ableton__*",
], { cwd: process.cwd() });

let out = "";
proc.stdout.on("data", d => out += d);
proc.on("close", () => console.log(JSON.parse(out)));
