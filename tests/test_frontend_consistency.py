import re
import os

def test_frontend_ids_consistency():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js_path = os.path.join(base_dir, "static", "js", "app.js")
    html_path = os.path.join(base_dir, "static", "index.html")

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Find static getElementById calls
    ids_js = set(re.findall(r'document\.getElementById\([\'"]([a-zA-Z0-9_\-]+)[\'"]\)', js))
    ids_html = set(re.findall(r'id=[\'"]([a-zA-Z0-9_\-]+)[\'"]', html))

    # Dynamic IDs constructed with string interpolation
    dynamic_prefixes = ("tab-", "tab-btn-", "panel-provider-", "story-item-", "badge-", "inbox-item-")
    missing = [i for i in ids_js if i not in ids_html and not any(i.startswith(p) for p in dynamic_prefixes)]

    assert missing == [], f"Found IDs in app.js that do not exist in index.html: {missing}"
