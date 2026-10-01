# How to Install LinkedIn Nexus Agent in ChatGPT (Custom GPT)

You can turn ChatGPT into your autonomous LinkedIn operator by creating a **Custom GPT** that executes actions directly on your local LinkedIn Nexus engine.

---

### Step 1: Start Nexus Agent with Local Tunneling (Optional for Remote Access)
If ChatGPT needs to talk to your local machine from OpenAI's cloud:
```bash
# Run your Nexus server
python run.py

# In another terminal, expose port 8000 via ngrok or cloudflare tunnel
ngrok http 8000
```
*(Copy your public URL, e.g. `https://xyz.ngrok-free.app`)*

---

### Step 2: Create a Custom GPT in ChatGPT
1. Go to [chatgpt.com/gpts/editor](https://chatgpt.com/gpts/editor).
2. **Name**: `LinkedIn Nexus Agent`
3. **Description**: `Autonomous LinkedIn engine with 82-rule humanizer writing gate, cognitive brain receipts, and feed reach eyes.`
4. **Instructions**: Copy and paste the prompt below:

```text
You are the ChatGPT interface for LinkedIn Nexus Agent.
Your role is to help the user write, audit, optimize, and publish high-performance LinkedIn posts.

CRITICAL WRITING RULES:
1. Strictly follow the 82 Humanizer Rules: Never use robotic words like 'delve', 'robust', 'game-changer', 'landscape', 'tapestry', 'pivotal', 'foster'.
2. Structure all posts for mobile readability: 1 to 2 sentence paragraphs, whitespace breaks.
3. Every claim must cite verified numbers, latencies, or architecture receipts from the Story Bank (Sultrix Trade OS, Shadow Stream, Shadow Voice, CRM, Raulf International).
4. Use the connected Actions to:
   - Call 'draftPost' to write posts with 82-rule audits.
   - Call 'scanFeed' to look into the live LinkedIn feed.
   - Call 'inspectUrl' to analyze any LinkedIn link.
   - Call 'draftCommentReply' to reply to comments.
   - Call 'getStoryBank' to pull real receipts.
```

---

### Step 3: Add Custom Actions
1. In the GPT Editor, scroll down to **Actions** → Click **Create new action**.
2. Click **Import from URL** or paste the contents of `integrations/chatgpt/openapi.yaml`.
3. If using ngrok, update the `servers` URL to your ngrok address:
   ```yaml
   servers:
     - url: https://xyz.ngrok-free.app
   ```
4. Save and publish your Custom GPT! You can now ask ChatGPT:
   - *"Draft a LinkedIn post about cutting order latency in Sultrix Trade OS"*
   - *"Scan my LinkedIn feed and tell me what creators are talking about today"*
