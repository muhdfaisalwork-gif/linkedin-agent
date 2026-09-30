# 🚀 NexusAgent — Autonomous LinkedIn AI Agent & Studio (2026 Edition)

<p align="center">
  <img src="https://img.shields.io/badge/LinkedIn_Skills-12_Integrated-0A66C2?logo=linkedin&logoColor=white" alt="12 LinkedIn Skills">
  <img src="https://img.shields.io/badge/OpenRouter-Free_Models_Supported-7C3AED" alt="OpenRouter Free Models">
  <img src="https://img.shields.io/badge/Writing_Engine-82_Rule_Humanizer-10B981" alt="82 Rules Humanizer">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Brain-Cognitive_Evolution-F59E0B" alt="Cognitive Brain">
</p>

**NexusAgent** is a production-grade, open-source, autonomous LinkedIn Agent Studio equipped with an evolving **Cognitive Brain**, **12 specialized LinkedIn marketing skills** (based on `sergebulaev/linkedin-skills`), an interactive **Performance Dashboard**, and strict adherence to the **82-Rule Human-Natural Writing Master Prompt**.

---

## ✨ Core Capabilities

### 1. 🧠 Cognitive Brain & Evolution System
- **Story Bank (Real Career Receipts)**: Stores verified projects, numbers, metrics, dates, and scars (pre-seeded with **Sultrix Trade OS**, **Shadow Stream**, **Shadow Voice**, **CRM Dashboard**, **Relyguru**, and **Raulf International LLC**). The agent always grounds drafts in real evidence and never invents fake metrics.
- **Voice Profile & Fingerprint**: Configurable tone, cadence (1-2 sentence paragraphs with whitespace for mobile clarity), preferred builder verbs (`built`, `shipped`, `measured`), and banned buzzwords.
- **Dynamic Heuristic Evolution**: Tracks empirical reach and engagement across hook formulas (F1–F20) and founder angles (A1–A10). Dynamically adjusts selection weights using Bayesian reinforcement.
- **Autonomous Self-Reflection**: Regularly reviews published post analytics, evaluates what worked and what flopped, and updates strategy memory.

### 2. 🛡️ Strict 82-Rule Human-Natural Writing Engine
- Programmatic & prompt-level enforcement of all 82 master rules:
  - **Zero AI Buzzwords**: Bans `delve`, `pivotal`, `robust`, `comprehensive`, `transformative`, `landscape`, `tapestry`, `leverage`, `foster`, `streamline`, `game-changer`, etc.
  - **Plain Human Verbs**: Automatically converts `utilize` → `use`, `facilitate` → `help`, `commence` → `start`, `showcase` → `show`.
  - **Punctuation & Rhythm**: Caps em-dashes at ≤ 1 per 100 words, removes artificial reveal bridges (`The result?`, `Plot twist:`), and breaks machine-flat rhythms.
  - **2026 LinkedIn Feed Heuristics**: Line 1 hook under 210 characters (before the fold). Never opens with a question (-34% reach penalty); prefers number-first statements (+34% reach lift).

### 3. 🎨 Visual Asset Generator (Image + Text)
- Every post ships with **both image and text**:
  - **AI Conceptual Art Engine**: Free, instant high-resolution rendering via Pollinations (Flux model).
  - **Typeset Quote-Card Canvas**: Pixel-crisp 1:1 square quote and stat cards rendered server-side with Pillow.

### 4. 👤 9-Point Profile Optimizer
- Interactive profile audit and rewriter:
  - **220-Char Headline Formula**: `[What You Do] | [Who You Help] [Achieve What Result]`
  - **7-Step About Section**: Hook in first 265 chars, problem statement, proof points, tech stack, and clear CTA.
  - **Featured Section Playbook**: 3 flagship products pinned.
  - **Experience Bullets**: `Action Verb + Specific System + Observable Metric`.
  - **Skills Strategy**: Top 3 pinned skills for search discovery.

### 5. 💬 2-Level Comment Sweeper & DM Inbox
- **Comment Sweeper**: Sweeps whole post threads, filters out low-value spam, and generates human replies with correct 2-level `parentComment` URN mapping.
- **Direct Message (Inbox) Manager**: Classifies inbound message intent (`client_lead`, `partnership`, `peer`, `recruiter`, `spam`) and drafts human, conversion-focused replies.

### 6. 🌐 Multi-Backend Execution
- **Browser Automation (Playwright)**: Direct, open-source browser engine that posts with image upload, updates Headline/About, sweeps comments, and manages DMs.
- **Publora REST API**: Fast auto-publishing integration (free 15 posts/month).
- **Manual Mode**: 1-click clipboard copy with direct LinkedIn permalink composer.

---

## ⚡ Quick Start

### 1. Launch with 1 Click (Windows)
Double click `launch.bat` in the project root:
```cmd
launch.bat
```

### 2. Launch with Python / uv
```bash
# Using uv (fastest)
uv run python run.py

# Or standard Python
pip install -r requirements.txt
python run.py
```
The dashboard will automatically open at `http://localhost:8000`.

---

## ⚙️ Environment Configuration (`.env`)

```ini
# OpenRouter API (Pre-configured with free models)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=inclusionai/ling-3.0-flash-sante:free
FALLBACK_MODELS=inclusionai/ling-3.0-flash-sante:free,liquid/lfm-2.5-2.6b:free,dots-studio/dots-3-note-preview:free,stealth/space-bunny-alpha,google/gemma-4-31b-it:free,google/gemma-4-26b-a4b-it:free

# Dashboard
HOST=127.0.0.1
PORT=8000

# Execution Mode: 'manual', 'browser', or 'publora'
LINKEDIN_EXECUTION_MODE=manual

# Optional Publora API
PUBLORA_API_KEY=
LINKEDIN_PLATFORM_ID=
```

---

## 🧪 Testing

Run the automated test suites:
```bash
# 82-Rule Humanizer Test
python -m tests.test_rules

# Cognitive Brain & Story Bank Test
python -m tests.test_brain

# Skills Contracts & Comment Filtering Test
python -m tests.test_skills

# Media Quote-Card Test
python -m tests.test_media

# Full End-to-End Pipeline Test
python -m tests.test_e2e
```

---

## 📂 Project Structure

```
g:\linkedin agent\
├── api\                  # FastAPI REST backend & route controllers
│   ├── app.py            # Main application & static mounts
│   └── routes\           # Posts, Profile, Brain, Comments, Inbox, Analytics, Settings
├── core\
│   ├── brain\            # Cognitive Brain, Story Bank, Voice Profile, Reflector
│   ├── db\               # SQLite database & initial seed data
│   ├── linkedin\         # Playwright Browser Agent, Publora Client, Dispatcher
│   ├── llm\              # OpenRouter API client with free model fallback chain
│   ├── media\            # Pollinations Flux AI Art & Pillow Quote-Card renderer
│   ├── rules\            # 82-Rule Strict Master Prompt & Humanizer Scrubber
│   ├── scheduler\        # Background autonomous scheduler
│   └── skills\           # 12 LinkedIn skills implementations & references
├── static\               # Web dashboard (HTML, CSS, JS with Chart.js & Lucide)
├── storage\              # SQLite database file and generated images
├── tests\                # Unit and end-to-end integration tests
├── .env                  # Environment configuration
├── launch.bat            # 1-click Windows launcher
├── requirements.txt      # Python dependencies
└── run.py                # Main server runner & browser launcher
```

---

## 📄 License
MIT License. Open-source and freely extensible.
