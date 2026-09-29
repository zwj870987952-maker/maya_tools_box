import { spawn } from "node:child_process";
import readline from "node:readline";

// Read-only setup probe. This file never calls the reset-consumption method.
const windows = process.platform === "win32";
const command = windows ? "cmd.exe" : "codex";
const args = windows ? ["/d", "/s", "/c", "codex app-server"] : ["app-server"];
const child = spawn(command, args, {
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true,
});

let finished = false;
const timer = setTimeout(() => finish(1, "App Server read timed out"), 20000);

function send(method, id, params) {
  const message = { method, ...(id === null ? {} : { id }), params };
  child.stdin.write(`${JSON.stringify(message)}\n`);
}

function finish(code, message) {
  if (finished) return;
  finished = true;
  clearTimeout(timer);
  if (message) (code ? console.error : console.log)(message);
  child.kill();
  process.exitCode = code;
}

child.on("error", (error) => finish(1, `Cannot start ${command}: ${error.message}`));
child.on("exit", (code) => {
  if (!finished) finish(1, `App Server exited before responding (${code})`);
});

const lines = readline.createInterface({ input: child.stdout });
lines.on("line", (line) => {
  let response;
  try {
    response = JSON.parse(line);
  } catch {
    return;
  }

  if (response.id === 0) {
    if (response.error) return finish(1, `Initialize failed: ${response.error.message}`);
    send("initialized", null, {});
    send("account/read", 1, { refreshToken: false });
    return;
  }
  if (response.id === 1) {
    if (response.error) return finish(1, `Account read failed: ${response.error.message}`);
    const account = response.result?.account;
    console.log(`Account auth: ${account?.type ?? "none"}; plan: ${account?.planType ?? "unknown"}`);
    send("account/rateLimits/read", 2, {});
    return;
  }
  if (response.id === 2) {
    if (response.error) return finish(1, `Rate-limit read failed: ${response.error.message}`);
    const result = response.result ?? {};
    const limits = result.rateLimitsByLimitId?.codex ?? result.rateLimits ?? {};
    const credits = result.rateLimitResetCredits ?? {};
    console.log(JSON.stringify({
      primary: limits.primary && {
        usedPercent: limits.primary.usedPercent,
        resetsAt: limits.primary.resetsAt,
      },
      secondary: limits.secondary && {
        usedPercent: limits.secondary.usedPercent,
        resetsAt: limits.secondary.resetsAt,
      },
      availableResetCount: credits.availableCount ?? null,
      resetExpirations: Array.isArray(credits.credits)
        ? credits.credits.map((credit) => credit.expiresAt)
        : null,
    }, null, 2));
    finish(0);
  }
});

send("initialize", 0, {
  clientInfo: {
    name: "maya_staging_reset_probe",
    title: "Maya staging reset probe",
    version: "1.0.0",
  },
});
