import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db.database import init_db, get_connection
from core.brain.brain import BrainManager

def test_brain_initialization_and_seeding():
    init_db()
    brain = BrainManager()
    stories = brain.get_story_bank()
    assert len(stories) >= 5

    # Check user projects
    titles = [s["title"] for s in stories]
    assert any("Sultrix Trade" in t for t in titles)
    assert any("Shadow Stream" in t for t in titles)
    assert any("Shadow Voice" in t for t in titles)

def test_story_retrieval_by_topic():
    brain = BrainManager()
    receipts = brain.get_relevant_receipts("trading platform and order routing")
    assert "Sultrix Trade" in receipts

def test_heuristic_evolution():
    brain = BrainManager()
    heuristics_before = {h["formula_code"]: h["weight"] for h in brain.get_heuristics()}

    # Simulate strong post performance for F7
    brain.record_post_performance(post_id=1, impressions=5000, likes=350, comments=80, reposts=30, saves=40)

    heuristics_after = {h["formula_code"]: h["weight"] for h in brain.get_heuristics()}
    assert "F7" in heuristics_after

if __name__ == "__main__":
    test_brain_initialization_and_seeding()
    test_story_retrieval_by_topic()
    test_heuristic_evolution()
    print("All Brain tests passed successfully!")
