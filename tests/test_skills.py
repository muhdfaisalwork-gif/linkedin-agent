import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.skills.post_writer import HOOK_FORMULAS, FOUNDER_ANGLES
from core.skills.reply_handler import ReplyHandler

def test_hook_formulas_count():
    assert len(HOOK_FORMULAS) == 20
    assert "F7" in HOOK_FORMULAS
    assert "F17" in HOOK_FORMULAS

def test_founder_angles_count():
    assert len(FOUNDER_ANGLES) == 10
    assert "A1" in FOUNDER_ANGLES
    assert "A10" in FOUNDER_ANGLES

def test_comment_filtering():
    # Mock ReplyHandler without LLM for filtering test
    handler = ReplyHandler(llm=None, brain=None)
    comments = [
        {"author": "Real User", "text": "What database are you using for the high concurrency stream?"},
        {"author": "Bot 1", "text": "great post thanks for sharing"},
        {"author": "Bot 2", "text": "100% agree"}
    ]
    actionable, filtered = handler.filter_comments(comments)
    assert len(actionable) == 1
    assert len(filtered) == 2
    assert actionable[0]["author"] == "Real User"

def test_comment_drafter_delegation():
    from unittest.mock import MagicMock
    from core.skills.comment_drafter import CommentDrafter
    from core.brain.brain import BrainManager

    mock_llm = MagicMock()
    mock_llm.generate_text.return_value = "We tuned the thread scheduler to eliminate lock convoy issues."
    drafter = CommentDrafter(llm=mock_llm, brain=BrainManager())

    reply = drafter.draft_reply(
        post_content="High throughput stream architecture",
        comment_text="How did you solve thread contention?",
        author_name="Sarah K."
    )
    assert reply["commenter"] == "Sarah K."
    assert "lock convoy" in reply["reply_draft"]
    assert reply["suggested_reaction"] in ("LIKE", "INTEREST", "PRAISE")

def test_inbox_handler_intent_normalization():
    from unittest.mock import MagicMock
    from core.skills.inbox_handler import InboxHandler
    from core.brain.brain import BrainManager

    mock_llm = MagicMock()
    # Test intent with extra words and markdown bold
    mock_llm.generate_text.return_value = "**INTENT:** Client Lead (Enterprise)\n\nREPLY: Let's discuss order latency requirements."
    inbox = InboxHandler(llm=mock_llm, brain=BrainManager())

    res = inbox.process_message(
        sender_name="John Doe",
        sender_title="VP of Engineering",
        message_text="We need to build a high performance matching engine."
    )
    assert res["intent"] == "client_lead"
    assert "order latency" in res["reply_draft"]

def test_repurposer_and_hook_extractor_empty():
    from core.skills.repurposer import Repurposer, HookExtractor
    from unittest.mock import MagicMock

    rep = Repurposer(llm=MagicMock())
    empty_rep = rep.repurpose_to_linkedin("")
    assert "provide source content" in empty_rep["repurposed_post"]

    extractor = HookExtractor(llm=MagicMock())
    empty_hook = extractor.extract_hook("")
    assert "provide post text" in empty_hook["formula_breakdown"]

