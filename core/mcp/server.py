import sys
import os
import json
import traceback
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.db.database import init_db
from core.llm.client import UniversalLLMClient
from core.brain.brain import BrainManager
from core.skills.post_writer import PostWriter
from core.skills.comment_drafter import CommentDrafter
from core.skills.reply_handler import ReplyHandler
from core.reach.feed_engine import ReachFeedEngine
from core.reach.reader import ReachReader
from core.linkedin.browser_agent import LinkedInBrowserAgent

class LinkedInNexusMCPServer:
    """
    JSON-RPC 2.0 Stdio MCP Server for LinkedIn Nexus Agent.
    Implements the standard Model Context Protocol (2024-11-05).
    """

    def __init__(self):
        init_db()
        self.llm = UniversalLLMClient()
        self.brain = BrainManager()
        self.browser_agent = LinkedInBrowserAgent()
        self.post_writer = PostWriter(self.llm, self.brain)
        self.comment_drafter = CommentDrafter(self.llm, self.brain)
        self.reply_handler = ReplyHandler(self.llm, self.brain)
        self.feed_engine = ReachFeedEngine(self.browser_agent)
        self.reader = ReachReader(self.browser_agent)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "draft_linkedin_post",
                "description": "Drafts a high-impact LinkedIn post strictly adhering to the 82 Humanizer Rules, grounded in verified Story Bank receipts (Sultrix Trade OS, Shadow Stream, etc.) with mobile spacing and no AI tells.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic or core premise of the post (e.g. 'How we reduced order routing latency to 420ms')."
                        },
                        "hook_formula": {
                            "type": "string",
                            "description": "Optional 2026 hook formula code (e.g. F7 for Contrast/Pivot, F10 for Ledger, F1 for Polarizing Stance). Defaults to optimal weight.",
                            "default": "F7"
                        },
                        "founder_angle": {
                            "type": "string",
                            "description": "Optional founder angle code (e.g. A5 for Raw Architecture, A1 for Anti-Consensus).",
                            "default": "A5"
                        },
                        "target_length": {
                            "type": "string",
                            "enum": ["short", "medium", "long"],
                            "description": "Target length of post (short: <150 words, medium: 150-250 words, long: 250-400 words).",
                            "default": "medium"
                        },
                        "image_type": {
                            "type": "string",
                            "enum": ["none", "quote_card", "ledger_table", "receipt_screenshot", "polaroid_diagram"],
                            "description": "Type of visual asset to generate alongside post.",
                            "default": "none"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "scan_linkedin_feed",
                "description": "Uses Agent Reach visual eyes to scan the live LinkedIn feed, extract recent creator posts, authors, reaction counts, and comments.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of feed posts to extract (1-10).",
                            "default": 5
                        }
                    }
                }
            },
            {
                "name": "inspect_linkedin_url",
                "description": "Reads and analyzes any LinkedIn post, profile, or external tech article via dual-backend (Jina Reader + Browser DOM) and generates strategic founder commentary angles.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Full URL of the LinkedIn post, profile, or web article to inspect."
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "reply_to_comment",
                "description": "Drafts a natural, human-like comment reply using the 82 rules and cognitive brain facts, avoiding generic 'Thanks for sharing' praise.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "post_context": {
                            "type": "string",
                            "description": "Context or snippet of the original post."
                        },
                        "comment_text": {
                            "type": "string",
                            "description": "The commenter's text to respond to."
                        },
                        "author_name": {
                            "type": "string",
                            "description": "Name of commenter.",
                            "default": "LinkedIn Member"
                        }
                    },
                    "required": ["post_context", "comment_text"]
                }
            },
            {
                "name": "get_story_bank_receipts",
                "description": "Retrieves verified builder receipts, metrics, and project history from the Cognitive Brain (Sultrix Trade OS, Shadow Stream, Shadow Voice, CRM, Raulf International) to ground statements in real proof.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search term (e.g. 'trading', 'video', 'streaming', 'latency')."
                        }
                    }
                }
            },
            {
                "name": "publish_linkedin_post",
                "description": "Publishes a post with optional image to LinkedIn via the active execution backend (browser automation or Publora API).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Final post text to publish."
                        },
                        "image_path": {
                            "type": "string",
                            "description": "Optional local filesystem path to an image to attach."
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "check_agent_status",
                "description": "Returns current agent health, active LLM provider (Ollama, OpenAI, Claude, Gemini, OpenRouter), and LinkedIn session authentication status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if tool_name == "draft_linkedin_post":
            topic = arguments.get("topic", "")
            hook = arguments.get("hook_formula", "F7")
            angle = arguments.get("founder_angle", "A5")
            length = arguments.get("target_length", "medium")
            image_type = arguments.get("image_type", "none")
            res = self.post_writer.draft_post(
                topic=topic,
                hook_code=hook,
                founder_angle_code=angle,
                target_length=length,
                visual_type=image_type
            )
            audit = res.get("audit", {})
            return (
                f"### Drafted LinkedIn Post (Flesch Score: {audit.get('score', 0)}/100):\n\n"
                f"{res.get('content', '')}\n\n"
                f"---\n"
                f"**Hook Formula**: {res.get('hook_formula')}\n"
                f"**Founder Angle**: {res.get('founder_angle')}\n"
                f"**82-Rule Audit**: {'✓ Compliant' if audit.get('is_compliant') else '⚠️ Minor Tells Detected'}\n"
                f"**Image Asset**: {res.get('image_url') or 'None'}"
            )

        elif tool_name == "scan_linkedin_feed":
            limit = int(arguments.get("limit", 5))
            res = self.feed_engine.scan_and_log_feed(limit=limit)
            if res.get("status") != "success":
                return f"Feed scan error: {res.get('message')}"
            posts = res.get("posts", [])
            lines = [f"### Scanned {len(posts)} LinkedIn Feed Updates:\n"]
            for idx, p in enumerate(posts[:limit], 1):
                lines.append(f"**{idx}. {p.get('author_name')}** ({p.get('author_headline', '')})")
                lines.append(f"Reactions: {p.get('reaction_count', 0)} | Comments: {p.get('comment_count', 0)}")
                lines.append(f"> {p.get('post_text', '')[:200]}...")
                lines.append("")
            return "\n".join(lines)

        elif tool_name == "inspect_linkedin_url":
            url = arguments.get("url", "")
            res = self.reader.read_url(url)
            if res.get("status") != "success":
                return f"Could not inspect URL: {res.get('message')}"
            title = res.get("title", "")
            content = res.get("content", "")
            # Synthesize quick summary
            analysis = self.llm.generate_text(
                f"Analyze this content for LinkedIn commentary angles. Identify core thesis, key stat, and contrarian founder angle:\n\n{content[:2000]}",
                temperature=0.3
            )
            return f"### Inspected: {title}\n**Backend**: {res.get('backend')}\n\n{analysis}"

        elif tool_name == "reply_to_comment":
            context = arguments.get("post_context", "")
            comment = arguments.get("comment_text", "")
            author = arguments.get("author_name", "LinkedIn Member")
            res = self.comment_drafter.draft_reply(
                post_content=context,
                comment_text=comment,
                author_name=author
            )
            return (
                f"### Suggested Reply for {author}:\n\n"
                f"{res.get('reply_text', '')}\n\n"
                f"**Intent**: {res.get('intent', 'general')}\n"
                f"**Reaction**: {res.get('suggested_reaction', 'LIKE')}"
            )

        elif tool_name == "get_story_bank_receipts":
            query = arguments.get("query", "")
            if query:
                stories = self.brain.get_relevant_stories(query)
            else:
                stories = self.brain.get_all_stories()
            lines = [f"### Verified Story Bank Receipts ({len(stories)} found):\n"]
            for s in stories:
                lines.append(f"• **{s['title']}** [{s['category']}] ({s['year_or_date']})")
                lines.append(f"  {s['detail']}")
                if s.get("metrics_receipts"):
                    lines.append(f"  *Metrics*: {s['metrics_receipts']}")
                if s.get("url"):
                    lines.append(f"  *Link*: {s['url']}")
                lines.append("")
            return "\n".join(lines)

        elif tool_name == "publish_linkedin_post":
            from core.linkedin.dispatcher import PostDispatcher
            dispatcher = PostDispatcher(self.browser_agent)
            content = arguments.get("content", "")
            image_path = arguments.get("image_path")
            res = dispatcher.publish_now(content=content, image_path=image_path)
            return f"Publish Status: {res.get('status')} - {res.get('message')}"

        elif tool_name == "check_agent_status":
            auth = self.browser_agent.is_authenticated()
            provider = self.llm.active_provider_name
            model = self.llm.current_model
            receipt_count = len(self.brain.get_all_stories())
            return (
                f"### LinkedIn Nexus Agent Status:\n"
                f"• Active LLM Provider: {provider.upper()} ({model})\n"
                f"• LinkedIn Session: {'✓ Authenticated' if auth else '⚠️ Not Connected'}\n"
                f"• Story Bank Receipts: {receipt_count} verified projects\n"
                f"• 82-Rule Writing Gate: ACTIVE\n"
                f"• Agent Reach Eyes: ACTIVE"
            )

        raise ValueError(f"Unknown tool: {tool_name}")

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "linkedin-nexus-agent",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result_text = self.execute_tool(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "isError": True,
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool {name}: {str(e)}\n{traceback.format_exc()}"
                            }
                        ]
                    }
                }

        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "prompts": [
                        {
                            "name": "founder_post_from_idea",
                            "description": "Transforms a raw thought into a high-engagement 82-rule LinkedIn post grounded in real numbers.",
                            "arguments": [
                                {"name": "idea", "description": "Raw thought, metric, or event", "required": True}
                            ]
                        },
                        {
                            "name": "audit_draft",
                            "description": "Audits a LinkedIn draft against the 82 Humanizer Rules and reports banned words, cadence, and Flesch score.",
                            "arguments": [
                                {"name": "draft", "description": "LinkedIn draft text to audit", "required": True}
                            ]
                        }
                    ]
                }
            }

        elif method == "prompts/get":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            if name == "founder_post_from_idea":
                idea = args.get("idea", "")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "description": "Founder post draft prompt",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": f"Use draft_linkedin_post to write an 82-rule compliant post about this idea: {idea}"
                                }
                            }
                        ]
                    }
                }
            elif name == "audit_draft":
                draft = args.get("draft", "")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "description": "Audit draft against 82 Humanizer Rules",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": f"Audit this draft against the 82 Humanizer Rules and check for banned words, rhythm, and Flesch score:\n\n{draft}"
                                }
                            }
                        ]
                    }
                }

        # Unknown method
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        return None

def run_stdio_server():
    """Runs the MCP server over standard input/output."""
    # Ensure stdout and stdin do not mangle unicode
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if hasattr(sys.stdin, 'reconfigure'):
        try:
            sys.stdin.reconfigure(encoding='utf-8')
        except Exception:
            pass

    server = LinkedInNexusMCPServer()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = server.handle_request(req)
            if res is not None:
                sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()
