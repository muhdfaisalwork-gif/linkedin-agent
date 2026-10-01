import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

def test_banned_words_detection():
    ai_text = "In today's digital landscape, we delve into pivotal solutions to leverage robust synergies and foster innovation."
    audit = RulesEngine.audit_text(ai_text)
    assert not audit["is_compliant"]
    assert audit["score"] < 80
    assert "delve" in audit["banned_words_found"]
    assert "pivotal" in audit["banned_words_found"]

def test_humanizer_scrub():
    ai_text = "We utilize this method to facilitate deployments and leverage our infrastructure."
    cleaned, audit = Humanizer.humanize_text(ai_text)
    assert "utilize" not in cleaned.lower()
    assert "facilitate" not in cleaned.lower()
    assert "use" in cleaned.lower()
    assert "help" in cleaned.lower()

def test_em_dash_cap():
    text_with_many_dashes = "We shipped the trade engine — cut latency — saved $4,000 — and tested it — in production."
    audit = RulesEngine.audit_text(text_with_many_dashes)
    assert audit["em_dash_count"] == 4
    # Clean it
    cleaned, clean_audit = Humanizer.humanize_text(text_with_many_dashes)
    assert clean_audit["em_dash_count"] <= 2

def test_flesch_reading_score():
    simple_text = "We built Sultrix Trade OS to route orders faster. It cut execution latency down to 420 milliseconds."
    score = RulesEngine.calculate_flesch(simple_text)
    assert score > 50.0

def test_case_preserving_replacement():
    capitalized_text = "Utilize this architecture to facilitate testing. DELVE into the metrics."
    cleaned, audit = Humanizer.humanize_text(capitalized_text)
    # Ensure capitalization is preserved
    assert cleaned.startswith("Use")
    assert "help testing" in cleaned
    assert "EXAMINE" in cleaned or "Look closely at" in cleaned

def test_assistant_preamble_stripping_preserves_human_sentences():
    # Real assistant talk with preamble should strip preamble
    with_preamble = "Sure, here is the post:\n\nOrder routing latency dropped to 420ms.\n\nLet's discuss how we eliminated mutex contention."
    cleaned, _ = Humanizer.humanize_text(with_preamble)
    assert not cleaned.startswith("Sure, here is")
    assert "Order routing latency" in cleaned
    assert "Let's discuss" in cleaned

    # Natural human single-sentence reply starting with Let's or I will should NOT be deleted
    single_sentence = "Let's connect next week to review the trade OS."
    cleaned_single, _ = Humanizer.humanize_text(single_sentence)
    assert cleaned_single == "Let's connect next week to review the trade OS."

    i_will_sentence = "I will share our complete benchmarks tomorrow."
    cleaned_i_will, _ = Humanizer.humanize_text(i_will_sentence)
    assert cleaned_i_will == "I will share our complete benchmarks tomorrow."

def test_unclosed_tags_stripping():
    # Model opened post but never closed it
    truncated_post = "<post>\nSultrix Trade OS dropped latency from 1200ms to 420ms."
    cleaned, _ = Humanizer.humanize_text(truncated_post)
    assert not cleaned.startswith("<post>")
    assert "Sultrix Trade OS dropped latency" in cleaned

    # Model had stray think tag
    stray_think = "<think>Planning the hook</think>\nHere is the real post about high throughput."
    cleaned_think, _ = Humanizer.humanize_text(stray_think)
    assert "<think>" not in cleaned_think
    assert "</think>" not in cleaned_think
    assert "Here is the real post" in cleaned_think


if __name__ == "__main__":
    test_banned_words_detection()
    test_humanizer_scrub()
    test_em_dash_cap()
    test_flesch_reading_score()
    test_case_preserving_replacement()
    print("All Rules tests passed successfully!")
