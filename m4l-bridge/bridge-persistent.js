const { spawn } = require("child_process");
const readline = require("readline");
const Max = require("max-api");

const CLAUDE_BIN = "/Users/brianear/.local/bin/claude";
const REPO_PATH = "/Users/brianear/proyectos/ableton-mcp";

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
