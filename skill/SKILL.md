---
name: linkedin-nexus-agent
description: >
  Autonomous LinkedIn Studio & Reach Engine. MUST USE when the user asks to write,
  audit, schedule, or publish LinkedIn posts; scan live feeds; analyze competitor
  posts or profiles; or draft human-natural replies using the 82 Humanizer Rules
  and verified Cognitive Brain receipts.
metadata:
  author: Muhd Faisal
  homepage: https://github.com/muhdfaisalwork-gif/linkedin-agent
  version: 1.0.0
compatibility:
  - Antigravity
  - Claude Code
  - Cursor
  - Windsurf
  - OpenClaw
---

# LinkedIn Nexus Agent Skill

Autonomous LinkedIn operating system with an evolving **Cognitive Brain**, **82-Rule Humanizer Gate**, and **Agent Reach Eyes**.

## When to Use This Skill
- **Drafting LinkedIn Posts**: When the user wants a post that sounds like a candid human builder, using 2026 hook formulas (F1 to F20) and founder angles (A1 to A8), with mobile spacing (1-2 sentences per block) and ZERO AI tells.
- **Scanning Feed & Trends**: To look into the live LinkedIn feed using Agent Reach eyes to see trending topics and discussions.
- **Deep-Dive URL Analysis**: To inspect any LinkedIn profile, post, or article link and extract strategic angles.
- **Replying to Comments**: To classify commenter intent and draft value-add replies citing real project receipts.
- **Citing Receipts**: To pull real metrics from Sultrix Trade OS (sub-500ms latency), Shadow Stream (high-concurrency video), Shadow Voice, and Raulf International.

## Available Capabilities & Tools

### 1. `draft_linkedin_post`
Drafts a post strictly passing the 82-rule humanizer audit.
```json
{
  "topic": "Cutting trading execution latency from 1.2s to 420ms in Sultrix Trade OS",
  "hook_formula": "F7",
  "founder_angle": "A5",
  "target_length": "medium",
  "image_type": "quote_card"
}
```

### 2. `scan_linkedin_feed`
Takes a visual snapshot of the LinkedIn feed and parses recent creator posts.
```json
{
  "limit": 5
}
```

### 3. `inspect_linkedin_url`
Reads any LinkedIn post or web article using dual-backend Reach router (Jina Reader + Browser DOM).
```json
{
  "url": "https://www.linkedin.com/posts/..."
}
```

### 4. `reply_to_comment`
Drafts human-natural comment reply using Cognitive Brain facts.
```json
{
  "post_context": "We moved our backend to async Go workers...",
  "comment_text": "Did you see any memory leak issues with garbage collection?",
  "author_name": "Senior SRE"
}
```

### 5. `get_story_bank_receipts`
Queries verified project receipts from SQLite.
```json
{
  "query": "streaming"
}
```

### 6. `publish_linkedin_post`
Publishes a post via the active execution backend (Playwright browser or Publora).
```json
{
  "content": "Full post text...",
  "image_path": "storage/images/sample.png"
}
```

## 82-Rule Humanizer Guardrails
1. **Never use AI cliché vocabulary**: *delve, tapestry, robust, pivotal, game-changer, landscape, foster, testament, beacon, paramount, leverage, vibrant*.
2. **Never use robotic transitions**: *Furthermore, Moreover, In conclusion, Ultimately, Indeed*.
3. **Format for mobile**: Single sentence paragraphs, natural line breaks, no dense walls of text.
4. **Anchor in real receipts**: Every claim must link to numbers, hours, dollars, or architecture details from the Story Bank.
