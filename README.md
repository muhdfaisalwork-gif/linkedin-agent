# 🔍 GitHub SEO Agent — Open-Source Repository Discoverability Engine

[![CI](https://github.com/github-seo-agent/github-seo-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/github-seo-agent/github-seo-agent/actions/workflows/ci.yml)
[![GitHub Packages](https://img.shields.io/badge/GitHub%20Packages-%40muhdfaisalwork--gif%2Fgithub--seo--agent-blue?logo=npm&logoColor=white)](https://github.com/muhdfaisalwork-gif/linkedin-agent/pkgs/npm/github-seo-agent)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter%20Free%20Models-purple.svg)](https://openrouter.ai/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-green.svg)](https://modelcontextprotocol.io/)

> Maximize stars, forks, and organic search traffic for any GitHub repository. Free & open-source.

## ✨ Features

- 💯 **0-100 SEO Health Score** with actionable checklist
- 🤖 **AI-Powered Launch Copy** synthesis with free Gemma 4 & Nemotron models
- 🚀 **Multi-channel Launch Packs** (Hacker News, Reddit, Twitter/X, Product Hunt, GitHub Releases)
- 🏥 **Community Health File Generator** (100% GitHub profile score)
- 🔌 **Claude Desktop & Cursor MCP Server** integration
- 📊 **FastAPI Web Dashboard**
- 💻 **CLI Tool** for terminal-native workflows

## 🚀 Quick Start

```bash
git clone https://github.com/your-username/github-seo-agent.git
cd github-seo-agent
pip install -r requirements.txt
python github_seo_agent.py audit
```

## 💻 CLI Usage

```bash
# Run a full repository audit
python github_seo_agent.py audit

# Generate launch copy for a specific channel
python github_seo_agent.py launch --channel hacker_news

# Generate Community Health files
python github_seo_agent.py community --apply
```

## 📦 Run via NPX & GitHub Packages

Install or run directly anywhere without cloning the repository:

```bash
# Configure registry for the @muhdfaisalwork-gif scope
npm config set @muhdfaisalwork-gif:registry https://npm.pkg.github.com

# Run repository audit directly with npx
npx @muhdfaisalwork-gif/github-seo-agent audit

# Generate launch copy
npx @muhdfaisalwork-gif/github-seo-agent launch --channel hacker_news

# Run MCP server for Claude Desktop / Cursor
npx @muhdfaisalwork-gif/github-seo-agent mcp

# Start web dashboard
npx @muhdfaisalwork-gif/github-seo-agent dashboard
```

## 🔌 MCP Integration

To add the GitHub SEO Agent to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "github-seo-agent": {
      "command": "npx",
      "args": ["-y", "@muhdfaisalwork-gif/github-seo-agent", "mcp"]
    }
  }
}
```

## 🏆 Showcase

- **LinkedIn Nexus Agent**: [https://github.com/muhdfaisalwork-gif/linkedin-agent](https://github.com/muhdfaisalwork-gif/linkedin-agent) — Autonomous LinkedIn Studio & Reach Engine
- **ShadowStream**: [https://github.com/muhdfaisalwork-gif/ShadowStream](https://github.com/muhdfaisalwork-gif/ShadowStream) — Edge-Accelerated Open-Source Streaming Platform

## 🏗️ Architecture

```mermaid
flowchart TD
    A[User / CI CD] -->|CLI / Web| B(GitHub SEO Agent Core)
    B --> C{Analyzer Engine}
    B --> D{AI Synthesizer}
    C -->|Fetch Repo Data| E[GitHub API]
    D -->|Prompt Models| F[OpenRouter API]
    F -->|Gemma 4 / Nemotron| D
    B --> G[Markdown/HTML Reports]
    B --> H[MCP Protocol Server]
    H -->|Integrations| I[Claude Desktop / Cursor]
```

## ⚖️ GitHub SEO Agent vs Manual Optimization

| Feature | Manual Optimization | GitHub SEO Agent |
|---------|--------------------|------------------|
| Speed   | Hours / Days       | Seconds          |
| Cost    | High (Time)        | Free             |
| Quality | Varies             | High (AI-driven) |
| Score   | Manual checklist   | Automated 0-100  |

## 🤝 Contributing
Short contributing guide: fork, clone, install requirements, run tests, submit PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
MIT License. See the [LICENSE](LICENSE) file for details.
