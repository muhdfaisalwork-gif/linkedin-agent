import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests
import multiprocessing
import uvicorn
from core.db.database import init_db

def run_server():
    init_db()
    uvicorn.run("api.app:app", host="127.0.0.1", port=8001, log_level="warning")

def test_endpoints():
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    time.sleep(3)  # wait for server to bind

    base = "http://127.0.0.1:8001"
    try:
        # 1. Test Dashboard HTML
        r = requests.get(f"{base}/")
        assert r.status_code == 200
        assert "LinkedIn Nexus Agent" in r.text
        print("[OK] GET / (Dashboard HTML served)")

        # 2. Test Settings
        r = requests.get(f"{base}/api/settings")
        assert r.status_code == 200
        data = r.json()
        assert "openrouter_api_key_set" in data
        print("[OK] GET /api/settings (Settings active)")

        # 3. Test Story Bank
        r = requests.get(f"{base}/api/brain/story-bank")
        assert r.status_code == 200
        stories = r.json()
        assert len(stories) >= 5
        print(f"[OK] GET /api/brain/story-bank ({len(stories)} verified stories)")

        # 4. Test Analytics Overview
        r = requests.get(f"{base}/api/analytics/overview")
        assert r.status_code == 200
        overview = r.json()
        assert "top_formulas" in overview
        print(f"[OK] GET /api/analytics/overview (Top formulas: {len(overview['top_formulas'])})")

        # 5. Test 82-Rule Humanizer Endpoint
        r = requests.post(f"{base}/api/posts/humanize", json={
            "text": "In today's digital landscape, we delve into pivotal solutions to leverage robust synergies."
        })
        assert r.status_code == 200
        h_data = r.json()
        assert "delve" not in h_data["humanized_text"].lower()
        print("[OK] POST /api/posts/humanize (AI buzzwords scrubbed)")

        # 6. Test Comment Sweeper
        r = requests.post(f"{base}/api/comments/sweep", json={
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
        r = requests.post(f"{base}/api/inbox/process", json={
            "sender_name": "Sarah Chen",
            "sender_title": "CTO at FinTech",
            "message_text": "We need custom trading execution like Sultrix Trade OS. Can you build this for our fund?"
        })
        assert r.status_code == 200
        dm_data = r.json()
        assert "reply_draft" in dm_data
        print(f"[OK] POST /api/inbox/process (Intent: {dm_data['intent']})")

        # 8. Test 7-Day Content Planner
        r = requests.post(f"{base}/api/planner/generate", json={
            "focus_topic": "Sultrix Trade OS & High Concurrency Streaming"
        })
        assert r.status_code == 200
        plan_data = r.json()
        assert "weekly_plan" in plan_data
        print("[OK] POST /api/planner/generate (7-day calendar generated)")

        # 9. Test Engager ICP Segmentation
        r = requests.post(f"{base}/api/analytics/segment-engagers", json={
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
        r = requests.post(f"{base}/api/posts/repurpose", json={
            "source_text": "We reduced order routing latency from 3.2s to 420ms by removing redundant DB transactions.",
            "source_type": "tweet"
        })
        assert r.status_code == 200
        rep_data = r.json()
        assert "repurposed_post" in rep_data
        print("[OK] POST /api/posts/repurpose (Multi-channel content repurposed)")

        # 11. Test External Post Comment Drafting (Skill #3)
        r = requests.post(f"{base}/api/comments/draft-external", json={
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
        # Add test story
        r = requests.post(f"{base}/api/brain/story-bank", json={
            "category": "Test Project",
            "title": "Temp Benchmark System",
            "detail": "Benchmarked order throughput under 50k concurrent requests",
            "metrics": "50k req/s, 12ms p99",
            "url": "https://example.com/bench",
            "year_or_date": "2026"
        })
        assert r.status_code == 200
        test_story_id = r.json()["story_id"]

        # Update test story (PUT)
        r = requests.put(f"{base}/api/brain/story-bank/{test_story_id}", json={
            "category": "Test Project Updated",
            "title": "Temp Benchmark System v2",
            "detail": "Benchmarked order throughput under 75k concurrent requests",
            "metrics": "75k req/s, 9ms p99",
            "url": "https://example.com/bench-v2",
            "year_or_date": "2026"
        })
        assert r.status_code == 200
        assert r.json()["status"] == "updated"

        # Delete test story (DELETE)
        r = requests.delete(f"{base}/api/brain/story-bank/{test_story_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"

        # Verify 404 on deleting non-existent story
        r = requests.delete(f"{base}/api/brain/story-bank/{test_story_id}")
        assert r.status_code == 404
        print("[OK] Story Bank PUT and DELETE lifecycle verified with 404 validation")

        # 14. Test Post Save, GET by ID, and DELETE by ID
        r = requests.post(f"{base}/api/posts/save", json={
            "topic": "Live Endpoint Test Post",
            "hook_formula": "F7 - Odd-Precision Money Ledger",
            "content": "Testing post persistence and deletion mechanics.",
            "status": "draft"
        })
        assert r.status_code == 200
        test_post_id = r.json()["post_id"]

        # GET post
        r = requests.get(f"{base}/api/posts/{test_post_id}")
        assert r.status_code == 200
        assert r.json()["topic"] == "Live Endpoint Test Post"

        # DELETE post
        r = requests.delete(f"{base}/api/posts/{test_post_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"

        # Verify 404
        r = requests.get(f"{base}/api/posts/{test_post_id}")
        assert r.status_code == 404
        print("[OK] Post GET and DELETE lifecycle verified with 404 validation")

        # 15. Test Inbox PATCH status and DELETE
        # Create inbox item
        r = requests.post(f"{base}/api/inbox/process", json={
            "sender_name": "Test Inbound Lead",
            "sender_title": "Product VP",
            "message_text": "Would like to discuss custom architecture services."
        })
        assert r.status_code == 200
        test_msg_id = r.json()["id"]

        # Update status (PATCH)
        r = requests.patch(f"{base}/api/inbox/{test_msg_id}", json={"status": "replied"})
        assert r.status_code == 200
        assert r.json()["new_status"] == "replied"

        # Delete message (DELETE)
        r = requests.delete(f"{base}/api/inbox/{test_msg_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"
        print("[OK] Inbox PATCH status and DELETE verified")

        print("\n[SUCCESS] ALL LIVE SERVER ENDPOINTS & LIFECYCLE TESTS VERIFIED AND PASSING!")

    finally:
        proc.terminate()
        proc.join()

if __name__ == "__main__":
    test_endpoints()
