import os
import json
import pytest
from unittest.mock import patch, MagicMock
from core.mcp.server import LinkedInNexusMCPServer

@pytest.fixture
def mcp_server():
    server = LinkedInNexusMCPServer()
    return server

def test_mcp_initialize(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    res = mcp_server.handle_request(req)
    assert res is not None
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == 1
    assert "result" in res
    result = res["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"]["name"] == "linkedin-nexus-agent"
    assert "tools" in result["capabilities"]
    assert "prompts" in result["capabilities"]

def test_mcp_ping(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "ping"
    }
    res = mcp_server.handle_request(req)
    assert res["result"] == {}

def test_mcp_tools_list(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/list"
    }
    res = mcp_server.handle_request(req)
    assert res is not None
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    expected_tools = [
        "draft_linkedin_post",
        "scan_linkedin_feed",
        "inspect_linkedin_url",
        "reply_to_comment",
        "get_story_bank_receipts",
        "publish_linkedin_post",
        "check_agent_status"
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Expected {expected} in MCP tools list"

def test_mcp_prompts_list(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list"
    }
    res = mcp_server.handle_request(req)
    assert res is not None
    prompts = res["result"]["prompts"]
    prompt_names = [p["name"] for p in prompts]
    assert "audit_draft" in prompt_names
    assert "founder_post_from_idea" in prompt_names

def test_mcp_call_check_agent_status(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "check_agent_status",
            "arguments": {}
        }
    }
    res = mcp_server.handle_request(req)
    assert "result" in res
    content = res["result"]["content"][0]["text"]
    assert "LinkedIn Nexus Agent Status" in content
    assert "Active LLM Provider" in content

def test_mcp_call_get_story_bank_receipts(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "get_story_bank_receipts",
            "arguments": {}
        }
    }
    res = mcp_server.handle_request(req)
    assert "result" in res
    content = res["result"]["content"][0]["text"]
    assert "Verified Story Bank Receipts" in content

def test_mcp_call_draft_linkedin_post_mocked(mcp_server):
    with patch.object(mcp_server.post_writer, "draft_post") as mock_writer:
        mock_writer.return_value = {
            "content": "Most engineering teams optimize for clean code.\n\nWe optimized for memory pressure.\n\nHere is how Sultrix Trade OS achieved 420ms latency.",
            "hook_formula": "F7",
            "founder_angle": "A5",
            "audit": {
                "score": 82,
                "is_compliant": True
            },
            "image_url": None
        }
        req = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "draft_linkedin_post",
                "arguments": {
                    "topic": "Sultrix latency"
                }
            }
        }
        res = mcp_server.handle_request(req)
        assert "result" in res
        content = res["result"]["content"][0]["text"]
        assert "Drafted LinkedIn Post" in content
        assert "Sultrix Trade OS" in content
        assert "F7" in content

def test_mcp_unknown_tool_error(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool",
            "arguments": {}
        }
    }
    res = mcp_server.handle_request(req)
    assert "result" in res
    assert res["result"].get("isError") is True
    assert "Unknown tool" in res["result"]["content"][0]["text"]

def test_mcp_http_endpoints():
    from fastapi.testclient import TestClient
    from api.app import app
    client = TestClient(app)

    # GET /mcp
    res_get = client.get("/mcp")
    assert res_get.status_code == 200
    assert res_get.json()["status"] == "online"
    assert len(res_get.json()["tools_available"]) >= 7

    # POST /mcp (JSON-RPC ping)
    res_post = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 100,
        "method": "ping"
    })
    assert res_post.status_code == 200
    assert res_post.json()["id"] == 100
    assert res_post.json()["result"] == {}

    # POST /api/mcp (tools/list)
    res_tools = client.post("/api/mcp", json={
        "jsonrpc": "2.0",
        "id": 101,
        "method": "tools/list"
    })
    assert res_tools.status_code == 200
    assert res_tools.json()["id"] == 101
    assert "tools" in res_tools.json()["result"]
