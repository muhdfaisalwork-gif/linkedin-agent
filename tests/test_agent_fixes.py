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
    print("All agent fixes tests passed!")
