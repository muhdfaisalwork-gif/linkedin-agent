#!/usr/bin/env node

/**
 * LinkedIn Nexus Agent — Node.js CLI Entry Point
 * Used by: npx @muhdfaisalwork-gif/linkedin-agent [command]
 */

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const projectRoot = path.resolve(__dirname, "..");

function findPython() {
  if (process.env.PYTHON_PATH) return process.env.PYTHON_PATH;

  // On Windows, check local app data python if python not directly on PATH
  if (process.platform === "win32") {
    const localPython = path.join(
      process.env.LOCALAPPDATA || "",
      "Python",
      "bin",
      "python.exe"
    );
    if (fs.existsSync(localPython)) {
      return localPython;
    }
  }

  return "python";
}

function printHelp() {
  console.log(`
🚀 LinkedIn Nexus Agent — Autonomous Open-Source Studio & MCP Engine
Package: @muhdfaisalwork-gif/linkedin-agent

Usage:
  npx @muhdfaisalwork-gif/linkedin-agent [command] [options]
  linkedin-agent [command] [options]

Commands:
  start          Start the autonomous studio dashboard (http://localhost:8000)
  mcp            Run the Claude Desktop / Cursor MCP stdio server
  audit          Run the GitHub SEO repository audit
  readme         Generate or apply search-optimized README
  launch         Generate viral multi-channel launch copy
  community      Generate GitHub Community Health standards files
  help           Show this help message

Options:
  --port <port>  Specify server port (default: 8000)
  --host <host>  Specify server host (default: 127.0.0.1)

Examples:
  npx @muhdfaisalwork-gif/linkedin-agent start
  npx @muhdfaisalwork-gif/linkedin-agent mcp
  npx @muhdfaisalwork-gif/linkedin-agent audit
  npx @muhdfaisalwork-gif/linkedin-agent launch --channel hacker_news
`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || "start";
  const pythonBin = findPython();

  if (command === "help" || command === "--help" || command === "-h") {
    printHelp();
    process.exit(0);
  }

  if (command === "start") {
    console.log("⚡ Starting LinkedIn Nexus Agent Studio...");
    const runScript = path.join(projectRoot, "run.py");

    const child = spawn(pythonBin, [runScript], {
      cwd: projectRoot,
      stdio: "inherit",
      env: process.env
    });

    child.on("error", (err) => {
      console.error(`Failed to launch Python server (${pythonBin}): ${err.message}`);
      console.error("Please ensure Python 3.10+ is installed and on your PATH.");
      process.exit(1);
    });

    child.on("exit", (code) => {
      process.exit(code || 0);
    });
    return;
  }

  if (command === "mcp") {
    const mcpScript = path.join(projectRoot, "run_mcp.py");

    const child = spawn(pythonBin, [mcpScript], {
      cwd: projectRoot,
      stdio: ["inherit", "inherit", "inherit"],
      env: process.env
    });

    child.on("error", (err) => {
      console.error(`Failed to launch MCP stdio server: ${err.message}`);
      process.exit(1);
    });

    child.on("exit", (code) => {
      process.exit(code || 0);
    });
    return;
  }

  if (["audit", "readme", "launch", "community"].includes(command)) {
    const seoScript = path.join(projectRoot, "scripts", "github_seo.py");
    if (fs.existsSync(seoScript)) {
      const child = spawn(pythonBin, [seoScript, ...args], {
        cwd: process.cwd(),
        stdio: "inherit",
        env: process.env
      });

      child.on("error", (err) => {
        console.error(`Failed to run SEO tool (${pythonBin}): ${err.message}`);
        process.exit(1);
      });

      child.on("exit", (code) => {
        process.exit(code || 0);
      });
      return;
    }
  }

  console.log(`Unknown command: ${command}`);
  printHelp();
  process.exit(1);
}

main().catch(err => {
  console.error("CLI error:", err);
  process.exit(1);
});
