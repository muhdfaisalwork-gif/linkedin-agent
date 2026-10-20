/**
 * GitHub SEO Agent — Node.js Client SDK & CLI Bridge
 * Published on GitHub Packages: @muhdfaisalwork-gif/github-seo-agent
 *
 * Programmatic SDK and execution bridge for GitHub repository discoverability,
 * AI-powered launch copy generation, community health scaffolding, and MCP server.
 */

const { spawn } = require("child_process");
const path = require("path");

class GitHubSEOClient {
  constructor(options = {}) {
    this.baseUrl = (options.baseUrl || process.env.GITHUB_SEO_URL || "http://127.0.0.1:8500").replace(/\/$/, "");
    this.timeout = options.timeout || 30000;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {
      const res = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });

      clearTimeout(timer);

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`GitHub SEO Agent API Error HTTP ${res.status}: ${text}`);
      }

      const contentType = res.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        return await res.json();
      }
      return await res.text();
    } catch (err) {
      clearTimeout(timer);
      throw err;
    }
  }

  // Health & Status
  async getHealth() {
    return this._request("/health");
  }

  // Audit
  async audit() {
    return this._request("/api/audit");
  }

  // README generator
  async generateReadme(params = {}) {
    return this._request("/api/readme", {
      method: "POST",
      body: JSON.stringify({
        project_name: params.projectName || params.project_name || "My Project",
        tagline: params.tagline || "",
        features: params.features || [],
        tech_stack: params.techStack || params.tech_stack || [],
        apply: Boolean(params.apply)
      })
    });
  }

  // Launch Pack
  async generateLaunchPack(params = {}) {
    return this._request("/api/launch", {
      method: "POST",
      body: JSON.stringify({
        channel: params.channel || "all",
        ai: Boolean(params.ai),
        angle: params.angle || "",
        model: params.model || "",
        repo_url: params.repoUrl || params.repo_url || "",
        project_name: params.projectName || params.project_name || "",
        features: params.features || []
      })
    });
  }

  // AI Launch copy synthesis
  async synthesizeAiLaunch(params = {}) {
    return this._request("/api/ai-launch", {
      method: "POST",
      body: JSON.stringify({
        channel: params.channel || "all",
        angle: params.angle || "",
        model: params.model || "",
        repo_url: params.repoUrl || params.repo_url || "",
        project_name: params.projectName || params.project_name || "",
        features: params.features || []
      })
    });
  }

  // Community health files
  async generateCommunityFiles(params = {}) {
    return this._request("/api/community", {
      method: "POST",
      body: JSON.stringify({
        apply: Boolean(params.apply)
      })
    });
  }

  // Subprocess runners
  static spawnDashboard(options = {}) {
    const rootDir = __dirname;
    const pythonExe = process.env.PYTHON_PATH || "python";
    const runScript = path.join(rootDir, "run.py");

    return spawn(pythonExe, [runScript], {
      cwd: rootDir,
      stdio: "inherit",
      env: { ...process.env, ...(options.env || {}) }
    });
  }

  static spawnMcp(options = {}) {
    const rootDir = __dirname;
    const pythonExe = process.env.PYTHON_PATH || "python";
    const mcpScript = path.join(rootDir, "run_mcp.py");

    return spawn(pythonExe, [mcpScript], {
      cwd: rootDir,
      stdio: ["inherit", "inherit", "inherit"],
      env: { ...process.env, ...(options.env || {}) }
    });
  }
}

module.exports = {
  GitHubSEOClient,
  default: GitHubSEOClient
};
