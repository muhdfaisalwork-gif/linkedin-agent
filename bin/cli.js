#!/usr/bin/env node

/**
 * GitHub SEO Agent — Node.js CLI Entry Point
 * Used by: npx @muhdfaisalwork-gif/github-seo-agent [command]
 */

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const projectRoot = path.resolve(__dirname, "..");

function findPython() {
  if (process.env.PYTHON_PATH) return process.env.PYTHON_PATH;

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
🔍 GitHub SEO Agent — Open-Source Discoverability & Launch Engine
Package: @muhdfaisalwork-gif/github-seo-agent

Usage:
  npx @muhdfaisalwork-gif/github-seo-agent [command] [options]
  github-seo-agent [command] [options]

Commands:
  audit          Run repository discoverability & health audit
  readme         Generate a high-converting search-optimized README.md
  launch         Generate launch copy (HN, Reddit, X/Twitter, Product Hunt)
  community      Generate GitHub community health files (CI, PR/Issue templates, etc.)
  mcp            Run the Claude Desktop / Cursor MCP stdio server
  dashboard      Start the FastAPI web dashboard (http://localhost:8500)
  help           Show this help message

Options:
  --repo-dir <path>     Target repository directory to audit (default: current directory)
  --channel <channel>   Launch channel: all, hacker_news, reddit, twitter_thread, product_hunt
  --ai                  Use OpenRouter AI for synthesis
  --apply               Write generated files directly to disk
  --port <port>         Dashboard port (default: 8500)

Examples:
  npx @muhdfaisalwork-gif/github-seo-agent audit
  npx @muhdfaisalwork-gif/github-seo-agent launch --channel hacker_news
  npx @muhdfaisalwork-gif/github-seo-agent mcp
  npx @muhdfaisalwork-gif/github-seo-agent dashboard
`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || "audit";
  const pythonBin = findPython();

  if (command === "help" || command === "--help" || command === "-h") {
    printHelp();
    process.exit(0);
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

  if (command === "dashboard" || command === "server") {
    console.log("⚡ Starting GitHub SEO Agent Web Dashboard...");
    const runScript = path.join(projectRoot, "run.py");
    const child = spawn(pythonBin, [runScript], {
      cwd: projectRoot,
      stdio: "inherit",
      env: process.env
    });

    child.on("error", (err) => {
      console.error(`Failed to launch dashboard server (${pythonBin}): ${err.message}`);
      process.exit(1);
    });

    child.on("exit", (code) => {
      process.exit(code || 0);
    });
    return;
  }

  // Forward command directly to python CLI (github_seo_agent.py)
  const cliScript = path.join(projectRoot, "github_seo_agent.py");
  const child = spawn(pythonBin, [cliScript, ...args], {
    cwd: process.cwd(),
    stdio: "inherit",
    env: process.env
  });

  child.on("error", (err) => {
    console.error(`Failed to run GitHub SEO Agent CLI (${pythonBin}): ${err.message}`);
    console.error("Please ensure Python 3.10+ is installed and on your PATH.");
    process.exit(1);
  });

  child.on("exit", (code) => {
    process.exit(code || 0);
  });
}

main().catch((err) => {
  console.error("Fatal Error:", err);
  process.exit(1);
});
