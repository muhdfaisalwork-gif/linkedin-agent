import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.database import init_db, get_connection
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.reach.reader import ReachReader
from core.reach.feed_engine import ReachFeedEngine
from api.app import app

client = TestClient(app)

def test_database_scanned_feed_posts_schema():
    init_db()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scanned_feed_posts'")
    table = c.fetchone()
    assert table is not None, "scanned_feed_posts table should exist in database"

    # Insert a mock post
    c.execute("""
        INSERT INTO scanned_feed_posts (
            author_name, author_headline, post_text, post_url, reaction_count, comment_count
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ("Test Creator", "Founder @ Stealth", "Testing Agent Reach visual feed inspection", "urn:li:activity:12345", 42, 7))
    conn.commit()

    c.execute("SELECT author_name, reaction_count FROM scanned_feed_posts WHERE post_url='urn:li:activity:12345'")
    row = c.fetchone()
    assert row["author_name"] == "Test Creator"
    assert row["reaction_count"] == 42
    conn.close()

def test_browser_agent_cookie_token_sanitization():
    agent = LinkedInBrowserAgent()
    # Invalid token length should fail fast without launching browser
    res_short = agent.save_cookie("abc")
    assert res_short["status"] == "error"

    # Disconnect should clear session
    res_disc = agent.disconnect()
    assert res_disc["status"] == "success"
    assert not agent.is_authenticated()

def test_reach_reader_url_handling():
    reader = ReachReader()
    # Test reading with mock or real public page
    res = reader.read_url("https://example.com")
    assert "status" in res
    assert "backend" in res

def test_reach_feed_engine_retrieval():
    engine = ReachFeedEngine()
    posts = engine.get_recent_scanned_posts(limit=5)
    assert isinstance(posts, list)

def test_api_settings_cookie_and_disconnect():
    # Disconnect endpoint
    res = client.post("/api/settings/disconnect")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Save cookie validation endpoint
    res_invalid = client.post("/api/settings/save-cookie", json={"cookie": "short"})
    assert res_invalid.status_code == 200
    assert res_invalid.json()["status"] == "error"

def test_api_reach_feed_endpoint():
    res = client.get("/api/reach/feed")
    assert res.status_code == 200
    data = res.json()
    assert "posts" in data
    assert "count" in data
