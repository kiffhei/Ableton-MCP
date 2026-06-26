const { spawn } = require("child_process");
const readline = require("readline");
const CLAUDE_BIN = "/Users/brianear/.local/bin/claude";

const claude = spawn(CLAUDE_BIN, [
  "-p", "--input-format", "stream-json", "--output-format", "stream-json",
  "--verbose", "--allowedTools", "mcp__ableton__*",
], { cwd: process.cwd() });

const rl = readline.createInterface({ input: claude.stdout });
const t0 = Date.now();
const ts = () => ((Date.now() - t0) / 1000).toFixed(1) + "s";

claude.stderr.on("data", d => console.error(`[stderr ${ts()}]`, d.toString()));

function send(text) {
  console.log(`[${ts()}] >> enviando: ${text}`);
  claude.stdin.write(JSON.stringify({
    type: "user", message: { role: "user", content: [{ type: "text", text }] }
  }) + "\n");
}

let turn = 0;
rl.on("line", (line) => {
  console.log(`[${ts()}] << raw: ${line}`);
  let msg;
  try { msg = JSON.parse(line); } catch { return; }
  if (msg.type === "result") {
    turn++;
    console.log(`[${ts()}] === RESULT turno ${turn}: ${msg.result}`);
    if (turn === 1) {
      send("Ahora bájalo a -12 dB");       // se manda SOLO cuando el turno 1 ya confirmó result
    } else if (turn === 2) {
      console.log(`[${ts()}] Test completo, cerrando proceso.`);
      claude.stdin.end();
    }
  }
});

send("Sube el volumen del track 0 a -6 dB");
