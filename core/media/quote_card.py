import os
import uuid
from PIL import Image, ImageDraw, ImageFont

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "images")
os.makedirs(STORAGE_DIR, exist_ok=True)

class QuoteCardRenderer:
    """Renders crisp, high-impact 1:1 square quote-cards for LinkedIn hooks."""

    @staticmethod
    def render_quote_card(
        quote: str,
        author_name: str = "Founder & Architect",
        handle: str = "@raulfinternational",
        theme: str = "dark"
    ) -> str:
        width = 1080
        height = 1080  # 1:1 square for feed

        bg_color = (15, 23, 42) if theme == "dark" else (248, 250, 252)
        text_color = (241, 245, 249) if theme == "dark" else (15, 23, 42)
        accent_color = (59, 130, 246)  # Blue-500
        muted_color = (148, 163, 184) if theme == "dark" else (100, 116, 139)

        img = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Load fonts with fallback
        try:
            quote_font = ImageFont.truetype("arial.ttf", 40)
            author_font = ImageFont.truetype("arial.ttf", 28)
            handle_font = ImageFont.truetype("arial.ttf", 22)
            quote_mark_font = ImageFont.truetype("arial.ttf", 80)
        except Exception:
            try:
                quote_font = ImageFont.load_default(size=40)
                author_font = ImageFont.load_default(size=28)
                handle_font = ImageFont.load_default(size=22)
                quote_mark_font = ImageFont.load_default(size=80)
            except TypeError:
                quote_font = ImageFont.load_default()
                author_font = quote_font
                handle_font = quote_font
                quote_mark_font = quote_font

        # Draw elegant corner accent line
        draw.line([(90, 90), (190, 90)], fill=accent_color, width=8)

        # Draw decorative quotation mark
        draw.text((90, 115), "“", fill=accent_color, font=quote_mark_font)

        # Truncate quote if extremely long so it fits comfortably
        clean_quote = quote.strip('“”"\' \n') or "Architecting high-scale distributed systems."
        if len(clean_quote) > 260:
            clean_quote = clean_quote[:257] + "..."

        # Word wrap text cleanly
        words = clean_quote.split()
        lines = []
        current_line = []
        max_chars_per_line = 36

        for word in words:
            if not current_line:
                current_line.append(word)
            elif sum(len(w) for w in current_line) + len(current_line) + len(word) <= max_chars_per_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        # Render lines centered vertically
        line_height = 58
        total_text_height = len(lines) * line_height
        start_y = max(230, (height - total_text_height) // 2 - 30)

        for i, line in enumerate(lines):
            y_pos = start_y + (i * line_height)
            draw.text((95, y_pos), line, fill=text_color, font=quote_font)

        # Draw separator line
        sep_y = start_y + total_text_height + 50
        draw.line([(95, sep_y), (width - 95, sep_y)], fill=(30, 41, 59) if theme == "dark" else (226, 232, 240), width=2)

        # Draw Author info
        draw.text((95, sep_y + 25), author_name, fill=text_color, font=author_font)
        draw.text((95, sep_y + 65), handle, fill=accent_color, font=handle_font)

        filename = f"card_{uuid.uuid4().hex[:10]}.png"
        filepath = os.path.join(STORAGE_DIR, filename)
        img.save(filepath, "PNG")

        return f"/storage/images/{filename}"
