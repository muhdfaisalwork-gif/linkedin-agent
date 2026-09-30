import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.media.quote_card import QuoteCardRenderer

def test_quote_card_rendering():
    card_url = QuoteCardRenderer.render_quote_card(
        quote="We cut order latency down from 1.2s to 420ms on Sultrix Trade OS.",
        author_name="Founder & Architect",
        handle="@raulfinternational"
    )
    assert card_url.startswith("/storage/images/")
    filename = card_url.split("/")[-1]
    storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "images", filename)
    assert os.path.exists(storage_path)

if __name__ == "__main__":
    test_quote_card_rendering()
    print("All Media tests passed successfully!")
