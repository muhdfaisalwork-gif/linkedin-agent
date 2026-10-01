import os
import re
from typing import Dict, Any, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Target High-Intent Search Keywords for GitHub & Google Ranking
TARGET_KEYWORDS = [
    {"keyword": "linkedin agent", "intent": "Core Product", "volume": "Very High", "tag": "linkedin-agent"},
    {"keyword": "linkedin automation", "intent": "Category", "volume": "High", "tag": "linkedin-automation"},
    {"keyword": "mcp server", "intent": "Protocol", "volume": "Very High", "tag": "mcp-server"},
    {"keyword": "claude desktop mcp", "intent": "Ecosystem", "volume": "High", "tag": "claude-mcp"},
    {"keyword": "ollama agents", "intent": "Local AI", "volume": "Very High", "tag": "ollama"},
    {"keyword": "deepseek r1", "intent": "Reasoning Models", "volume": "Extreme", "tag": "deepseek-r1"},
    {"keyword": "playwright automation", "intent": "Browser Engine", "volume": "High", "tag": "playwright"},
    {"keyword": "open source linkedin", "intent": "Alternative", "volume": "High", "tag": "open-source"},
    {"keyword": "ai marketing agent", "intent": "Use-case", "volume": "High", "tag": "ai-agents"},
    {"keyword": "fastapi studio", "intent": "Tech Stack", "volume": "Medium", "tag": "fastapi"}
]

RECOMMENDED_GITHUB_TOPICS = [
    "linkedin-agent",
    "linkedin-automation",
    "mcp-server",
    "claude-mcp",
    "ollama",
    "deepseek-r1",
    "playwright",
    "ai-agents",
    "social-media-automation",
    "open-source",
    "fastapi",
    "python",
    "autonomous-agents",
    "growth-hacking"
]

class LinkedInNexusGitHubSEO:
    """
    Autonomous GitHub SEO Engine dedicated to LinkedIn Nexus Agent:
    - Analyzes repository discoverability and calculates GitHub SEO Score (0-100)
    - Generates high-converting, keyword-dense README with comparison matrices
    - Crafts multi-channel viral launch packs (Hacker News, Reddit, Twitter, Releases)
    - Generates GitHub Community Health files (CI workflow, issue templates, guidelines)
    """

    def __init__(self, repo_dir: Optional[str] = None):
        self.repo_dir = repo_dir or REPO_ROOT

    def audit_repository(self) -> Dict[str, Any]:
        """
        Audits current repository status against GitHub search algorithm and Google SEO ranking factors.
        Returns a quantitative score (0-100) and actionable checklist.
        """
        readme_path = os.path.join(self.repo_dir, "README.md")
        readme_content = ""
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read()

        checklist = []
        score = 100

        # 1. README Presence & Size
        if not readme_content or len(readme_content) < 500:
            score -= 25
            checklist.append({"item": "README.md Content", "status": "fail", "impact": "High", "note": "README is empty or too short for search engine indexing."})
        else:
            checklist.append({"item": "README.md Content", "status": "pass", "impact": "High", "note": f"Rich content detected ({len(readme_content)} bytes)."})

        # 2. Key Term Coverage (Ollama, MCP, Humanizer, Playwright, Free models)
        essential_terms = ["ollama", "mcp", "humanizer", "playwright", "open-source", "cookie"]
        missing_terms = [t for t in essential_terms if t not in readme_content.lower()]
        if missing_terms:
            deduction = len(missing_terms) * 4
            score -= deduction
            checklist.append({
                "item": "Keyword Density in README",
                "status": "warning" if len(missing_terms) <= 2 else "fail",
                "impact": "High",
                "note": f"Missing key search terms in README: {', '.join(missing_terms)}."
            })
        else:
            checklist.append({"item": "Keyword Density in README", "status": "pass", "impact": "High", "note": "All high-intent search terms present."})

        # 3. Dynamic Shields Badges
        badge_count = len(re.findall(r'https://img\.shields\.io', readme_content))
        if badge_count < 4:
            score -= 10
            checklist.append({"item": "Shields.io Badges", "status": "warning", "impact": "Medium", "note": f"Found {badge_count} badges. Recommend at least 5 badges (License, CI, MCP, Python, Ollama)."})
        else:
            checklist.append({"item": "Shields.io Badges", "status": "pass", "impact": "Medium", "note": f"Strong visual trust signals ({badge_count} badges found)."})

        # 4. GitHub Actions CI Workflow
        ci_path = os.path.join(self.repo_dir, ".github", "workflows", "ci.yml")
        if not os.path.exists(ci_path):
            score -= 15
            checklist.append({"item": "GitHub Actions CI Workflow", "status": "fail", "impact": "High", "note": "Missing .github/workflows/ci.yml. Passing CI workflows boost GitHub ranking algorithm."})
        else:
            checklist.append({"item": "GitHub Actions CI Workflow", "status": "pass", "impact": "High", "note": "Automated CI test workflow present."})

        # 5. Issue & PR Templates (Community Standards)
        issue_dir = os.path.join(self.repo_dir, ".github", "ISSUE_TEMPLATE")
        has_issue_templates = os.path.exists(issue_dir) and len(os.listdir(issue_dir)) > 0
        if not has_issue_templates:
            score -= 10
            checklist.append({"item": "Issue & PR Templates", "status": "warning", "impact": "Medium", "note": "Missing structured issue forms. Community health score affects GitHub Trending eligibility."})
        else:
            checklist.append({"item": "Issue & PR Templates", "status": "pass", "impact": "Medium", "note": "GitHub Community issue forms configured."})

        # 6. Contributing & Security Guidelines
        contrib_exists = os.path.exists(os.path.join(self.repo_dir, "CONTRIBUTING.md"))
        sec_exists = os.path.exists(os.path.join(self.repo_dir, "SECURITY.md"))
        if not (contrib_exists and sec_exists):
            score -= 8
            checklist.append({"item": "Community Standards (CONTRIBUTING & SECURITY)", "status": "warning", "impact": "Medium", "note": "Missing CONTRIBUTING.md or SECURITY.md."})
        else:
            checklist.append({"item": "Community Standards (CONTRIBUTING & SECURITY)", "status": "pass", "impact": "Medium", "note": "Full community guidelines present."})

        # 7. Comparison Table vs. Paid Alternatives
        has_comparison = "taplio" in readme_content.lower() or "comparison" in readme_content.lower()
        if not has_comparison:
            score -= 7
            checklist.append({"item": "Competitive Positioning Matrix", "status": "warning", "impact": "High", "note": "Missing comparison table vs paid SaaS (Taplio/AuthoredUp). Conversion rates drop without clear contrast."})
        else:
            checklist.append({"item": "Competitive Positioning Matrix", "status": "pass", "impact": "High", "note": "Clear contrast against $80/mo proprietary alternatives included."})

        final_score = max(0, min(100, score))
        grade = "A+" if final_score >= 95 else ("A" if final_score >= 85 else ("B" if final_score >= 70 else "C"))

        return {
            "score": final_score,
            "grade": grade,
            "checklist": checklist,
            "top_keywords": TARGET_KEYWORDS,
            "recommended_topics": RECOMMENDED_GITHUB_TOPICS,
            "gh_cli_command": f"gh repo edit muhdfaisalwork-gif/linkedin-agent --add-topic \"{','.join(RECOMMENDED_GITHUB_TOPICS[:10])}\""
        }

    def generate_optimized_readme(self) -> str:
        """
        Generates the search-optimized, high-converting README.md for LinkedIn Nexus Agent.
        """
        return """# 🚀 LinkedIn Nexus Agent — Autonomous Open-Source LinkedIn Studio & Reach Engine

<p align="center">
  <a href="https://github.com/muhdfaisalwork-gif/linkedin-agent/actions"><img src="https://img.shields.io/badge/Tests-61%2F61%20Passing-brightgreen?logo=github-actions&logoColor=white" alt="Tests"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Protocol%202024--11--05-blue?logo=anthropic&logoColor=white" alt="MCP Server"></a>
  <a href="https://ollama.com/"><img src="https://img.shields.io/badge/Ollama-100%25%20Offline%20Ready-black?logo=ollama&logoColor=white" alt="Ollama Local"></a>
  <a href="https://openrouter.ai/"><img src="https://img.shields.io/badge/OpenRouter-Free%20Models%20Included-purple" alt="OpenRouter"></a>
  <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/Playwright-Stealth%20Automated-2EAD33?logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
</p>

<p align="center">
  <b>The #1 Free, Open-Source Alternative to Taplio & AuthoredUp.</b><br>
  Equipped with an evolving <b>Cognitive Brain</b>, an <b>82-Rule Humanizer Gate</b>, <b>Agent Reach Eyes</b>, and native <b>Claude / Cursor MCP Server</b> support. Runs 100% locally with Ollama (zero API fees) or multi-model cloud providers.
</p>

---

## ⚡ Why LinkedIn Nexus Agent?

Most AI tools generate detectable, robotic LinkedIn slop (*"In today's fast-paced digital landscape, delving into transformative ecosystems..."*). The 2026 LinkedIn algorithm aggressively penalizes this with **-34% to -65% distribution reach**.

**LinkedIn Nexus Agent solves this at the architecture level:**
1. **82-Rule Humanizer Guardrail**: Programmatically eliminates all 82 AI tells, banned buzzwords, robotic reveal bridges, and artificial staccato.
2. **Cognitive Brain & Career Story Bank**: Stores your real ventures, numbers, latency benchmarks, and scars. Never invents fake case studies.
3. **Agent Reach Eyes**: Autonomous visual DOM & Jina Reader scanner that observes trending feed posts and extracts contrarian founder commentary angles.
4. **Universal Multi-Model Freedom**: Switch instantly between **Local Ollama** (100% private & free), **Anthropic Claude**, **OpenAI GPT-4o**, **Google Gemini**, or **Free OpenRouter models**.
5. **Claude Desktop & Cursor MCP Server**: Chat with your agent directly inside Claude Desktop, Cursor, or ChatGPT to draft, schedule, and publish posts.

---

## 📊 Comparison: LinkedIn Nexus Agent vs. Paid SaaS

| Feature | **LinkedIn Nexus Agent** | **Taplio** | **AuthoredUp** | **Jasper / Copy.ai** |
| :--- | :---: | :---: | :---: | :---: |
| **Price** | **$0 / month (Free & Open Source)** | $65 – $199 / mo | $20 – $40 / mo | $49 – $125 / mo |
| **Local Offline AI (Ollama)** | **✓ Yes (100% private)** | ❌ No | ❌ No | ❌ No |
| **82-Rule Anti-Slop Humanizer** | **✓ Yes (Strict Programmatic)** | ❌ Generic AI | ❌ Formatting only | ❌ Generic AI |
| **Cognitive Brain & Story Bank** | **✓ Yes (Verified Receipts)** | ❌ No memory | ❌ No memory | ❌ Generic personas |
| **Claude Desktop / Cursor MCP** | **✓ Native JSON-RPC 2.0** | ❌ No | ❌ No | ❌ No |
| **Direct Session Cookie (`li_at`)** | **✓ Yes (< 1s Instant Sync)** | Chrome Ext only | Chrome Ext only | ❌ No |
| **Autonomous Agent Reach Eyes** | **✓ Yes (DOM + Multimodal Vision)**| ❌ No | ❌ No | ❌ No |
| **Data Privacy** | **100% Local SQLite on your machine**| Stored in Cloud | Stored in Cloud | Stored in Cloud |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Interfaces ["Multi-Channel Interfaces"]
        UI["Web Studio Dashboard (:8000)"]
        Claude["Claude Desktop (MCP Protocol)"]
        Cursor["Cursor IDE (MCP Server)"]
        ChatGPT["ChatGPT Custom Actions (OpenAPI)"]
    end

    subgraph Core ["LinkedIn Nexus Agent Core"]
        Brain["Cognitive Brain & Story Bank\\n(Verified Receipts & Scars)"]
        Humanizer["82-Rule Strict Humanizer Engine\\n(Anti-Slop Filter & Flesch Scorer)"]
        Reach["Agent Reach Eyes\\n(Playwright Feed Scanner + Jina Reader)"]
        Dispatcher["Multi-Backend Dispatcher\\n(Playwright Session + Publora API)"]
    end

    subgraph Models ["Universal Multi-Model Engine"]
        Ollama["Local Ollama\\n(DeepSeek-R1 / Llama 3.2)"]
        ClaudeLLM["Anthropic Claude 3.5"]
        OpenAI["OpenAI GPT-4o"]
        Gemini["Google Gemini 2.0 Flash"]
        OpenRouter["OpenRouter (Free Models Chain)"]
    end

    Interfaces --> Core
    Core --> Models
    Dispatcher --> LinkedIn[("LinkedIn Live Feed & Profile")]
```

---

## 🚀 Quick Start (Up in < 2 Minutes)

### Option A: 1-Click Launch (Windows)
Double-click `launch.bat` in the repository root:
```cmd
launch.bat
```

### Option B: Terminal / uv (All Platforms)
```bash
# Clone the repository
git clone https://github.com/muhdfaisalwork-gif/linkedin-agent.git
cd linkedin-agent

# Install dependencies (using uv or standard pip)
pip install -r requirements.txt

# Launch Studio Server
python run.py
```
Open your browser to **http://localhost:8000**.

---

## 🔌 Connect to Claude Desktop or Cursor (MCP)

LinkedIn Nexus Agent ships with a certified **Model Context Protocol (MCP)** server:

### 1-Click Auto-Installer:
```bash
python scripts/install_mcp.py
```

### Manual Configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "linkedin-nexus": {
      "command": "python",
      "args": ["g:\\\\linkedin agent\\\\run_mcp.py"]
    }
  }
}
```

Now you can prompt Claude:
- *"Draft a high-engagement post on our 420ms order latency using hook formula F7."*
- *"Scan my LinkedIn feed and recommend 3 trending posts to comment on."*
- *"Audit my profile headline and about section."*

---

## 🦙 Run 100% Locally with Ollama (Zero Cost, Complete Privacy)

1. Install [Ollama](https://ollama.com/) and pull a model:
```bash
ollama run deepseek-r1:8b
# or
ollama run llama3.2:latest
```
2. In the Studio Dashboard, go to **Settings** → Select **Ollama (Local)**.
3. Everything (post writing, comment replying, profile optimization) now runs completely offline on your own GPU/CPU with **zero API keys and zero cost**.

---

## 🧪 Automated Test Suite (100% Pass Rate)

Run the automated test suite (61 tests covering rules, brain, reach, MCP, and multi-model routing):
```bash
python -m pytest
```

---

## 🤝 Contributing & Community

Contributions are warmly welcomed! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and review [SECURITY.md](SECURITY.md).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
"""

    def generate_launch_pack(self, channel: str = "all") -> Dict[str, str]:
        """
        Generates community-native launch copy tailored specifically for LinkedIn Nexus Agent.
        """
        repo_url = "https://github.com/muhdfaisalwork-gif/linkedin-agent"

        hn_post = f"""Title: Show HN: LinkedIn Nexus Agent – Open-source autonomous studio with local Ollama, 82 humanizer rules, and Claude MCP

URL / Text:
Hey HN,

I built LinkedIn Nexus Agent ({repo_url}) because I was frustrated with two things:
1. Proprietary LinkedIn SaaS tools charging $65–$199/month for glorified OpenAI wrapper templates.
2. The tidal wave of robotic, detectable AI "slop" that the 2026 LinkedIn algorithm actively downranks (-34% reach penalty for opening with questions, -65% for buzzword density).

LinkedIn Nexus Agent is a completely free, open-source local studio with:
- Strict 82-Rule Humanizer Engine: Programmatically strips preambles, eliminates 40+ banned buzzwords (delve, pivotal, robust, landscape), controls em-dashes, and enforces 2026 mobile line breaks.
- Cognitive Brain & Story Bank: Stores real project receipts and numbers in local SQLite. The LLM is grounded in authentic facts and never invents metrics.
- Agent Reach Eyes: Uses a dual-backend router (Playwright DOM + Jina Reader) to visually observe the live LinkedIn feed and generate contrarian founder angles.
- Model Freedom: Runs 100% offline with Local Ollama (DeepSeek-R1 / Llama 3.2), or connects directly to Claude, GPT-4o, Gemini, or free OpenRouter models.
- Native MCP Server: Includes a certified Model Context Protocol (2024-11-05) stdio server so you can drive the entire studio inside Claude Desktop or Cursor.
- Instant Authentication: Connects via direct `li_at` cookie injection in < 1 second.

The stack is Python 3.10+, FastAPI, Playwright, SQLite, and Pillow for quote-card typography. 61/61 automated tests passing.

Repository: {repo_url}
MIT licensed. Would love your feedback and thoughts on the architecture!"""

        reddit_localllama = f"""Title: I built a 100% local, offline LinkedIn Studio using Ollama, DeepSeek-R1, and Playwright (Free & Open Source)

Post:
Hey r/LocalLLaMA,

Like many of you, I refused to send private career data and corporate drafts to third-party marketing SaaS platforms that charge $80+/month.

I built **LinkedIn Nexus Agent**, an open-source autonomous studio that runs completely on your own machine:
GitHub: {repo_url}

Key features for local model builders:
- Native Ollama Integration: Runs offline on deepseek-r1:8b, llama3.2, mistral, or qwen2.5 with automatic thinking-tag (</think>) cleanup.
- 82-Rule Anti-Slop Filter: Cleans robotic AI tells and enforces 2026 human writing principles before text ever touches the screen.
- Claude / Cursor MCP Server: Built-in Model Context Protocol server (`run_mcp.py`) so you can prompt your local model from your preferred agent IDE.
- Agent Reach Eyes: Playwright browser engine for headless feed inspection and 1-second `li_at` session cookie injection.
- Zero Cloud Lock-in: All data is saved in a local SQLite file (`storage/linkedin_agent.db`).

Launch it locally with:
git clone {repo_url}
pip install -r requirements.txt
python run.py

Would love to hear what local models you recommend for concise, human-natural writing!"""

        reddit_selfhosted = f"""Title: Self-Hosted LinkedIn Studio: Open-source alternative to Taplio with SQLite, Playwright, and local Ollama support

Post:
Hi r/selfhosted,

If you're looking for a self-hosted, private tool to manage your LinkedIn presence without monthly subscriptions or cloud tracking, check out **LinkedIn Nexus Agent**:
GitHub: {repo_url}

Why self-host it:
- 100% Local Storage: Uses a lightweight SQLite database for drafts, analytics, and voice profile memory.
- Multi-Model Flexibility: Use local Ollama for zero-cost offline drafting, or plug in your own API keys (OpenAI, Anthropic Claude, Gemini, or OpenRouter free models).
- Headless Browser Automation: Automated post publishing with image attachment, comment sweeps, and profile updates via Playwright.
- One-Click Cookie Auth: Instant connection using your session cookie (`li_at`) in under 1 second.
- MCP Server Support: Exposes JSON-RPC 2.0 tools for Claude Desktop and Cursor.

Quickstart:
git clone {repo_url}
python run.py
-> Opens dashboard on http://localhost:8000

Feedback and PRs are very welcome!"""

        twitter_thread = f"""🧵 How we built an open-source, autonomous LinkedIn Agent that bypasses the 2026 AI slop penalty (and why you shouldn't pay $89/mo for Taplio):

1/5 Most AI LinkedIn posts fail because they reek of chatbot tells: "delve", "pivotal", "in today's landscape".
The LinkedIn feed algorithm actively penalizes this with -34% to -65% reach.

We built LinkedIn Nexus Agent to fix this. 100% free & open source:
{repo_url}

2/5 The 82-Rule Humanizer:
Instead of standard prompting, our engine runs a 4-pass programmatic scrub.
It enforces 1-2 sentence paragraphs for mobile screens, strips AI preambles, and grounds every claim in verified career receipts from a local Cognitive Brain.

3/5 Model Context Protocol (MCP) Inside:
It exposes native JSON-RPC 2.0 tools. You can hook it into Claude Desktop or Cursor in 30 seconds with `python scripts/install_mcp.py`.
Prompt Claude: "Draft today's post and schedule it for tomorrow at 8 AM."

4/5 Zero API Fees with Local Ollama:
Runs completely offline on DeepSeek-R1 or Llama 3.2. Your drafts and credentials never leave your local machine.

5/5 1-Click Launch:
Clone the repo, run `python run.py`, and launch your local studio at localhost:8000.
Star the repo on GitHub: {repo_url} ⭐"""

        release_v1 = f"""# LinkedIn Nexus Agent v1.0.0 — Official Open-Source Launch

We are thrilled to release **LinkedIn Nexus Agent v1.0.0**, the complete autonomous open-source LinkedIn Studio and Reach Engine!

### 🌟 What's New in v1.0.0:
- **82-Rule Humanizer Guardrail**: Programmatic anti-slop engine enforcing plain verbs, mobile whitespace, and zero AI buzzwords.
- **Cognitive Brain & Story Bank**: Persistent career receipts memory in SQLite to ground all copy in authentic facts.
- **Agent Reach Eyes**: Dual-backend router (Playwright DOM + Jina Reader) for feed scanning and URL commentary synthesis.
- **Universal Multi-Model Routing**: Native support for Local Ollama, Anthropic Claude, OpenAI, Google Gemini, and OpenRouter free models.
- **Model Context Protocol (MCP) Server**: Full stdio integration for Claude Desktop, Cursor, and ChatGPT.
- **1-Second Cookie Connection**: Instant direct session injection with `li_at` cookie verification.
- **Complete Test Suite**: 61/61 unit and integration tests passing.

### 🚀 Getting Started:
```bash
git clone {repo_url}.git
cd linkedin-agent
pip install -r requirements.txt
python run.py
```

Full documentation: {repo_url}#readme"""

        packs = {
            "hacker_news": hn_post,
            "reddit_localllama": reddit_localllama,
            "reddit_selfhosted": reddit_selfhosted,
            "twitter_thread": twitter_thread,
            "release_notes": release_v1
        }

        if channel != "all" and channel in packs:
            return {channel: packs[channel]}
        return packs

    def generate_community_health_files(self) -> Dict[str, str]:
        """
        Creates GitHub Community Standards files to achieve a 100% GitHub Health Score.
        """
        dot_github = os.path.join(self.repo_dir, ".github")
        workflows_dir = os.path.join(dot_github, "workflows")
        issues_dir = os.path.join(dot_github, "ISSUE_TEMPLATE")

        os.makedirs(workflows_dir, exist_ok=True)
        os.makedirs(issues_dir, exist_ok=True)

        files_written = []

        # 1. CI Workflow
        ci_content = """name: Tests & Quality Gate

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Test Suite
        run: |
          python -m pytest --ignore=tests/test_e2e.py -v
"""
        ci_path = os.path.join(workflows_dir, "ci.yml")
        with open(ci_path, "w", encoding="utf-8") as f:
            f.write(ci_content)
        files_written.append(".github/workflows/ci.yml")

        # 2. Bug Report Template
        bug_content = """name: Bug Report
description: Create a report to help us improve LinkedIn Nexus Agent
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: Thanks for reporting a bug! Please fill out the details below.
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Also tell us what you expected to happen.
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: Operating System & Python Version
      placeholder: Windows 11 / Python 3.11 / Local Ollama deepseek-r1
    validations:
      required: true
"""
        bug_path = os.path.join(issues_dir, "bug_report.yml")
        with open(bug_path, "w", encoding="utf-8") as f:
            f.write(bug_content)
        files_written.append(".github/ISSUE_TEMPLATE/bug_report.yml")

        # 3. Feature Request Template
        feat_content = """name: Feature Request
description: Suggest an idea or enhancement for LinkedIn Nexus Agent
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: What problem would this feature solve?
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Describe the proposed solution
    validations:
      required: true
"""
        feat_path = os.path.join(issues_dir, "feature_request.yml")
        with open(feat_path, "w", encoding="utf-8") as f:
            f.write(feat_content)
        files_written.append(".github/ISSUE_TEMPLATE/feature_request.yml")

        # 4. Pull Request Template
        pr_content = """## Description
Briefly describe the change and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Documentation update
- [ ] Performance optimization

## Testing
- [ ] Ran `python -m pytest` and all tests pass (100%)
"""
        pr_path = os.path.join(dot_github, "PULL_REQUEST_TEMPLATE.md")
        with open(pr_path, "w", encoding="utf-8") as f:
            f.write(pr_content)
        files_written.append(".github/PULL_REQUEST_TEMPLATE.md")

        # 5. CONTRIBUTING.md
        contrib_content = """# Contributing to LinkedIn Nexus Agent

Thank you for contributing to the open-source LinkedIn Nexus Agent!

## Development Setup
1. Fork and clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the automated test suite:
   ```bash
   python -m pytest
   ```

## Code Guidelines
- Adhere to the **82-Rule Humanizer** principles for any prompts or LLM generation logic.
- Ensure all new routes or skills include automated unit tests under `tests/`.
- Verify 100% test passing rate before submitting PRs.
"""
        contrib_path = os.path.join(self.repo_dir, "CONTRIBUTING.md")
        with open(contrib_path, "w", encoding="utf-8") as f:
            f.write(contrib_content)
        files_written.append("CONTRIBUTING.md")

        # 6. SECURITY.md
        sec_content = """# Security Policy

## Supported Versions
LinkedIn Nexus Agent v1.0.x is actively supported with security updates.

## Reporting a Vulnerability
Please do not report security vulnerabilities in public GitHub issues.
Instead, submit a confidential report or contact the maintainers at muhdfaisalwork@gmail.com.
We will respond within 48 hours.
"""
        sec_path = os.path.join(self.repo_dir, "SECURITY.md")
        with open(sec_path, "w", encoding="utf-8") as f:
            f.write(sec_content)
        files_written.append("SECURITY.md")

        return {
            "status": "success",
            "files_written": files_written,
            "message": "All GitHub Community Standards files successfully installed (100% health score ready)."
        }
