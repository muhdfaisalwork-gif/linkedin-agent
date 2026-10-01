import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.app import app
from core.db.database import init_db

client = TestClient(app)

def fake_generate_text(self, prompt, system_prompt=None, temperature=0.7):
    p_lower = prompt.lower()
    if "classify intent" in p_lower or "inbound message" in p_lower:
        return "INTENT: client_lead\nREPLY: We built Sultrix Trade OS to handle real-time order routing."
    elif "weekly content plan" in p_lower or "weekly_plan" in p_lower or "planner" in p_lower:
        return '{"weekly_plan": [{"day": "Monday", "hook_formula": "F7", "topic": "Latency", "angle": "Boring tech"}]}'
    elif "repurpose" in p_lower or "source_text" in p_lower or "tweet" in p_lower:
        return "We cut order latency to 420ms on Sultrix Trade OS. Simple architecture wins."
    elif "comment" in p_lower or "external" in p_lower:
        return "Great observation on event queues. We saw similar throughput gains with thread pinning."
    elif "write a linkedin post" in p_lower:
        return "<post>\n$14,200/month saved on cloud bills by cutting order latency to 420ms.\n\nWe rebuilt the matching engine for Sultrix Trade OS.\n\nWhat is your latency budget?\n</post>"
    return "Mock response for system validation."

@patch("core.llm.client.UniversalLLMClient.generate_text", new=fake_generate_text)
def test_endpoints():
    init_db()

    # 1. Test Dashboard HTML
    r = client.get("/")
    assert r.status_code == 200
    assert "LinkedIn Nexus Agent" in r.text
    print("[OK] GET / (Dashboard HTML served)")

    # 2. Test Settings
    r = client.get("/api/settings")
    assert r.status_code == 200
    data = r.json()
    assert "openrouter_api_key_set" in data
    print("[OK] GET /api/settings (Settings active)")

    # 3. Test Story Bank
    r = client.get("/api/brain/story-bank")
    assert r.status_code == 200
    stories = r.json()
    assert len(stories) >= 5
    print(f"[OK] GET /api/brain/story-bank ({len(stories)} verified stories)")

    # 4. Test Analytics Overview
    r = client.get("/api/analytics/overview")
    assert r.status_code == 200
    overview = r.json()
    assert "top_formulas" in overview
    print(f"[OK] GET /api/analytics/overview (Top formulas: {len(overview['top_formulas'])})")

    # 5. Test 82-Rule Humanizer Endpoint
    r = client.post("/api/posts/humanize", json={
        "text": "In today's digital landscape, we delve into pivotal solutions to leverage robust synergies."
    })
    assert r.status_code == 200
    h_data = r.json()
    assert "delve" not in h_data["humanized_text"].lower()
    print("[OK] POST /api/posts/humanize (AI buzzwords scrubbed)")

    # 6. Test Comment Sweeper
    r = client.post("/api/comments/sweep", json={
        "post_context": "Sultrix Trade OS cut order latency to 420ms.",
        "sample_comments": [
            {"author": "Dev", "text": "Are you using Redis or Kafka for message queueing?", "depth": 1, "top_level_urn": "urn:li:comment:1"},
            {"author": "Bot", "text": "great post thanks for sharing", "depth": 1}
        ]
    })
    assert r.status_code == 200
    sweep_data = r.json()
    assert sweep_data["filtered_count"] == 1
    assert sweep_data["actionable_count"] == 1
    print("[OK] POST /api/comments/sweep (2-level comment sweep & spam filter verified)")

    # 7. Test Inbound DM Classifier
    r = client.post("/api/inbox/process", json={
        "sender_name": "Sarah Chen",
        "sender_title": "CTO at FinTech",
        "message_text": "We need custom trading execution like Sultrix Trade OS. Can you build this for our fund?"
    })
    assert r.status_code == 200
    dm_data = r.json()
    assert "reply_draft" in dm_data
    print(f"[OK] POST /api/inbox/process (Intent: {dm_data['intent']})")

    # 8. Test 7-Day Content Planner
    r = client.post("/api/planner/generate", json={
        "focus_topic": "Sultrix Trade OS & High Concurrency Streaming"
    })
    assert r.status_code == 200
    plan_data = r.json()
    assert "weekly_plan" in plan_data
    print("[OK] POST /api/planner/generate (7-day calendar generated)")

    # 9. Test Engager ICP Segmentation
    r = client.post("/api/analytics/segment-engagers", json={
        "engagers": [
            {"name": "Alice Johnson", "title": "VP of Engineering at Stripe"},
            {"name": "Bob Smith", "title": "Senior Backend Developer"}
        ]
    })
    assert r.status_code == 200
    seg_data = r.json()
    assert seg_data["prospects_count"] == 1
    assert seg_data["peers_count"] == 1
    print("[OK] POST /api/analytics/segment-engagers (ICP segmentation verified)")

    # 10. Test Content Repurposing
    r = client.post("/api/posts/repurpose", json={
        "source_text": "We reduced order routing latency from 3.2s to 420ms by removing redundant DB transactions.",
        "source_type": "tweet"
    })
    assert r.status_code == 200
    rep_data = r.json()
    assert "repurposed_post" in rep_data
    print("[OK] POST /api/posts/repurpose (Multi-channel content repurposed)")

    # 11. Test External Post Comment Drafting (Skill #3)
    r = client.post("/api/comments/draft-external", json={
        "post_text": "We just migrated our entire pipeline to asynchronous event queues. How are others handling message ordering?",
        "author_name": "Senior Staff Architect"
    })
    assert r.status_code == 200
    ext_comment = r.json()
    assert "comment_draft" in ext_comment
    print("[OK] POST /api/comments/draft-external (Thoughtful comment drafted)")

    # 12. Test Empty Text Audit Resilience
    from core.rules.rules_engine import RulesEngine
    empty_audit = RulesEngine.audit_text("")
    assert empty_audit["is_compliant"] is True
    assert empty_audit["flesch_score"] == 70.0
    assert empty_audit["em_dash_count"] == 0
    print("[OK] RulesEngine.audit_text('') (Empty text audit schema resilient)")

    # 13. Test Story Bank PUT, GET, and DELETE Lifecycle
    r = client.post("/api/brain/story-bank", json={
        "category": "Test Project",
        "title": "Temp Benchmark System",
        "detail": "Benchmarked order throughput under 50k concurrent requests",
        "metrics": "50k req/s, 12ms p99",
        "url": "https://example.com/bench"
    })
    assert r.status_code == 200
    created_story = r.json()
    test_id = created_story.get("story_id") or created_story.get("id")
    print(f"[OK] Story Bank POST created id={test_id}")

    # Verify story exists in list
    r = client.get("/api/brain/story-bank")
    assert r.status_code == 200
    all_stories = r.json()
    found = any(s["id"] == test_id for s in all_stories)
    assert found is True
    print(f"[OK] Story Bank GET confirmed id={test_id}")

    # Delete story
    r = client.delete(f"/api/brain/story-bank/{test_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"
    print(f"[OK] Story Bank DELETE removed id={test_id}")

    # 14. Test Posts Save, GET, and DELETE Lifecycle
    r = client.post("/api/posts/save", json={
        "topic": "Live Endpoint Test Post",
        "hook_formula": "F7 - Odd-Precision Money Ledger",
        "content": "$14,200/month saved on cloud bills by cutting latency to 420ms.",
        "image_url": "/storage/images/sample.png",
        "image_type": "quote_card",
        "status": "draft"
    })
    assert r.status_code == 200
    post_res = r.json()
    test_post_id = post_res["post_id"]
    print(f"[OK] Post created with id={test_post_id}")

    # GET post
    r = client.get(f"/api/posts/{test_post_id}")
    assert r.status_code == 200
    assert r.json()["topic"] == "Live Endpoint Test Post"

    # DELETE post
    r = client.delete(f"/api/posts/{test_post_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    # Verify 404
    r = client.get(f"/api/posts/{test_post_id}")
    assert r.status_code == 404
    print("[OK] Post GET and DELETE lifecycle verified with 404 validation")

    # 15. Test Inbox PATCH status and DELETE
    r = client.post("/api/inbox/process", json={
        "sender_name": "Test Inbound Lead",
        "sender_title": "Product VP",
        "message_text": "Would like to discuss custom architecture services."
    })
    assert r.status_code == 200
    test_msg_id = r.json()["id"]

    # Update status (PATCH)
    r = client.patch(f"/api/inbox/{test_msg_id}", json={"status": "replied"})
    assert r.status_code == 200
    assert r.json()["new_status"] == "replied"

    # Delete message (DELETE)
    r = client.delete(f"/api/inbox/{test_msg_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"
    print("[OK] Inbox PATCH status and DELETE verified")

    print("\n[SUCCESS] ALL LIVE SERVER ENDPOINTS & LIFECYCLE TESTS VERIFIED AND PASSING!")

if __name__ == "__main__":
    test_endpoints()
