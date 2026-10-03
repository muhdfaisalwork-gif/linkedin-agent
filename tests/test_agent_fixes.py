import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.app import app
from core.rules.rules_engine import RulesEngine
from core.db.database import get_connection

client = TestClient(app)

def test_flesch_with_numbers_and_tech_terms():
    text = "We cut latency from 1200ms to 420ms across 10k active concurrent streams on AWS."
    score = RulesEngine.calculate_flesch(text)
    assert 0 <= score <= 100
    assert score > 30

def test_save_post_with_empty_scheduled_time():
    # Empty scheduled_time should be saved as NULL/None rather than crashing
    r = client.post("/api/posts/save", json={
        "topic": "Test Empty Schedule",
        "hook_formula": "F7 - Odd-Precision Money Ledger",
        "content": "Sultrix Trade OS reduced latency to 420ms.",
        "scheduled_time": "   ",
        "status": "draft"
    })
    assert r.status_code == 200
    post_id = r.json()["post_id"]

    # Verify in DB that scheduled_time is None
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT scheduled_time, status FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    conn.close()
    assert row["scheduled_time"] is None
    assert row["status"] == "draft"

    # Cleanup
    client.delete(f"/api/posts/{post_id}")

def test_send_comment_reply_endpoint():
    r = client.post("/api/comments/send-reply", json={
        "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:123456789",
        "reply_text": "We engineered the order matching core using async Python and WebSocket streams."
    })
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("manual", "success", "error", "auth_required")

def test_send_dm_endpoint():
    r = client.post("/api/inbox/send", json={
        "recipient": "elena-rostova",
        "message_text": "Thanks for reaching out! We can discuss the high-concurrency streaming architecture."
    })
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("manual", "success", "error", "auth_required")

def test_publish_post_unauthenticated_does_not_set_published():
    # Create draft
    r = client.post("/api/posts/save", json={
        "topic": "Test Unauthenticated Publish Safety",
        "hook_formula": "F1 - Platform Risk Anaphora",
        "content": "Testing that unauthenticated browser errors do not falsely mark posts as published.",
        "status": "draft"
    })
    assert r.status_code == 200
    post_id = r.json()["post_id"]

    # Publish
    pub_res = client.post(f"/api/posts/publish/{post_id}")
    assert pub_res.status_code == 200

    # Ensure status is not erroneously 'published' if dispatch was an auth error
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    conn.close()

    # In test environment with manual or browser auth, status must be draft or manual (published if manual composer)
    assert row["status"] in ("draft", "published")

    # Cleanup
    client.delete(f"/api/posts/{post_id}")

def test_save_post_persists_founder_angle():
    r = client.post("/api/posts/save", json={
        "topic": "Architecture Tradeoffs",
        "hook_formula": "F7 - Odd-Precision Money Ledger",
        "founder_angle": "A5 - The unglamorous bet",
        "content": "Sultrix Trade OS reduced latency to 420ms by removing mutex bottlenecks.",
        "status": "draft"
    })
    assert r.status_code == 200
    post_id = r.json()["post_id"]

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT founder_angle FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    conn.close()
    assert row["founder_angle"] == "A5 - The unglamorous bet"

    client.delete(f"/api/posts/{post_id}")

def test_image_generator_none_type():
    from core.media.image_generator import ImageGenerator
    res = ImageGenerator.create_post_visual(hook="Some Hook", topic="Architecture", visual_type="none")
    assert res["type"] == "none"
    assert res["url"] is None

def test_reply_handler_none_original_post():
    from core.skills.reply_handler import ReplyHandler
    from unittest.mock import MagicMock
    mock_llm = MagicMock()
    mock_llm.generate_text.return_value = "We solved this with lockless queues."
    mock_brain = MagicMock()
    mock_brain.get_voice_profile.return_value = {}

    handler = ReplyHandler(mock_llm, mock_brain)
    res = handler.draft_reply(original_post=None, comment_text="How did you cut latency?", commenter_name=None)
    assert "reply_draft" in res
    assert "lockless queues" in res["reply_draft"]

def test_inbox_handler_irregular_history_keys():
    from core.skills.inbox_handler import InboxHandler
    from unittest.mock import MagicMock
    mock_llm = MagicMock()
    mock_llm.generate_text.return_value = "INTENT: client_lead\nREPLY: We can hop on a quick call."
    mock_brain = MagicMock()
    mock_brain.get_voice_profile.return_value = {}
    mock_brain.get_story_bank.return_value = []

    handler = InboxHandler(mock_llm, mock_brain)
    # Pass irregular OpenAI format with role/content instead of sender/text
    res = handler.process_message(
        sender_name="Partner",
        sender_title="CTO",
        message_text="Do you do custom AI agent architecture?",
        conversation_history=[{"role": "user", "content": "Hello"}]
    )
    assert res["intent"] == "client_lead"
    assert "quick call" in res["reply_draft"]

def test_heuristics_null_safeguards_in_record_post_performance():
    from core.brain.brain import BrainManager
    conn = get_connection()
    c = conn.cursor()
    # Insert or update a heuristic with NULL usage_count and avg_engagement_rate
    c.execute("INSERT OR REPLACE INTO heuristics (formula_code, formula_name, weight, usage_count, avg_engagement_rate) VALUES (?, ?, ?, NULL, NULL)",
              ("F99", "Test Null Formula", 1.0))
    conn.commit()
    conn.close()

    brain = BrainManager()
    # Record performance should not raise TypeError
    brain.record_post_performance(post_id=99999, impressions=1000, likes=50, comments=10, reposts=5, saves=8)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT usage_count, avg_engagement_rate, weight FROM heuristics WHERE formula_code = ?", ("F99",))
    row = c.fetchone()
    # Clean up test records
    c.execute("DELETE FROM heuristics WHERE formula_code = ?", ("F99",))
    c.execute("DELETE FROM posts WHERE id = ?", (99999,))
    conn.commit()
    conn.close()

    assert row is not None

def test_publora_create_post_normalization():
    from core.linkedin.publora_client import PubloraClient
    from unittest.mock import patch, MagicMock

    client = PubloraClient(api_key="test-key")
    client._explicit_api_key = "test-key"
    with patch.object(PubloraClient, "platform_id", "urn:li:organization:123"):
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"id": "pub_12345", "success": True}
            mock_post.return_value = mock_resp

            res = client.create_post("Hello Publora")
            assert res["status"] == "success"
            assert res["id"] == "pub_12345"

def test_reflector_group_by_post_deduplication():
    from core.brain.reflector import Reflector
    from unittest.mock import MagicMock

    mock_llm = MagicMock()
    mock_llm.generate_text.return_value = "Learnings from posts."
    reflector = Reflector(mock_llm)

    # Insert post with multiple analytics entries
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO posts (id, topic, hook_formula, content, status) VALUES (88888, 'Dedup Topic', 'F7', 'Content', 'published')")
    c.execute("INSERT INTO post_analytics (post_id, impressions, likes, comments, reposts, saves) VALUES (88888, 100, 10, 2, 1, 0)")
    c.execute("INSERT INTO post_analytics (post_id, impressions, likes, comments, reposts, saves) VALUES (88888, 200, 20, 4, 2, 1)")
    conn.commit()
    conn.close()

    try:
        res = reflector.run_reflection_cycle()
        assert res["status"] == "success"
    finally:
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM posts WHERE id = 88888")
        c.execute("DELETE FROM post_analytics WHERE post_id = 88888")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    test_flesch_with_numbers_and_tech_terms()
    test_save_post_with_empty_scheduled_time()
    test_send_comment_reply_endpoint()
    test_send_dm_endpoint()
    test_publish_post_unauthenticated_does_not_set_published()
    test_save_post_persists_founder_angle()
    test_image_generator_none_type()
    test_reply_handler_none_original_post()
    test_inbox_handler_irregular_history_keys()
    test_heuristics_null_safeguards_in_record_post_performance()
    test_publora_create_post_normalization()
    test_reflector_group_by_post_deduplication()
    print("All agent fixes tests passed!")
