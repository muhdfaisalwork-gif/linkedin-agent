/**
 * LinkedIn Nexus Agent — Node.js Client SDK & CLI Bridge
 * Published on GitHub Packages: @muhdfaisalwork-gif/linkedin-agent
 *
 * Connects JavaScript/TypeScript applications and tools to LinkedIn Nexus Agent's
 * autonomous studio, 82-rule humanizer, cognitive brain, and MCP server.
 */

const { spawn } = require("child_process");
const path = require("path");

class LinkedInNexusClient {
  constructor(options = {}) {
    this.baseUrl = (options.baseUrl || process.env.LINKEDIN_AGENT_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
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
        throw new Error(`LinkedIn Agent API Error HTTP ${res.status}: ${text}`);
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

  // Health and System
  async getHealth() {
    return this._request("/health");
  }

  async getSettings() {
    return this._request("/api/settings");
  }

  // Post Studio
  async listPosts() {
    return this._request("/api/posts");
  }

  async getPost(id) {
    return this._request(`/api/posts/${id}`);
  }

  async generatePost(params) {
    return this._request("/api/posts/generate", {
      method: "POST",
      body: JSON.stringify({
        topic: params.topic,
        hook_code: params.hook_code || "F7",
        founder_angle_code: params.founder_angle_code || null,
        target_length: params.target_length || "medium",
        visual_type: params.visual_type || "ai_image"
      })
    });
  }

  async savePost(postData) {
    return this._request("/api/posts/save", {
      method: "POST",
      body: JSON.stringify(postData)
    });
  }

  async publishPost(id) {
    return this._request(`/api/posts/publish/${id}`, {
      method: "POST"
    });
  }

  async humanize(text) {
    return this._request("/api/posts/humanize", {
      method: "POST",
      body: JSON.stringify({ text })
    });
  }

  // Analytics & Brain
  async getAnalytics() {
    return this._request("/api/analytics/overview");
  }

  async getBrainStatus() {
    return this._request("/api/brain/status");
  }

  // GitHub SEO
  async getSeoAudit() {
    return this._request("/api/seo/audit");
  }

  async generateLaunchPack(channel = "all") {
    return this._request("/api/seo/launch-pack", {
      method: "POST",
      body: JSON.stringify({ channel })
    });
  }

  // Reach & Feed
  async scanFeed() {
    return this._request("/api/reach/scan-feed", { method: "POST" });
  }

  async inspectUrl(url) {
    return this._request("/api/reach/inspect", {
      method: "POST",
      body: JSON.stringify({ url })
    });
  }

  // Subprocess runners
  static spawnStudio(options = {}) {
    const rootDir = __dirname;
    const pythonExe = process.env.PYTHON_PATH || "python";
    const runScript = path.join(rootDir, "run.py");

    const child = spawn(pythonExe, [runScript], {
      cwd: rootDir,
      stdio: "inherit",
      env: { ...process.env, ...(options.env || {}) }
    });

    return child;
  }

  static spawnMcp(options = {}) {
    const rootDir = __dirname;
    const pythonExe = process.env.PYTHON_PATH || "python";
    const mcpScript = path.join(rootDir, "run_mcp.py");

    const child = spawn(pythonExe, [mcpScript], {
      cwd: rootDir,
      stdio: ["inherit", "inherit", "inherit"],
      env: { ...process.env, ...(options.env || {}) }
    });

    return child;
  }
}

module.exports = {
  LinkedInNexusClient,
  default: LinkedInNexusClient
};
