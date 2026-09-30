import re
from typing import Dict, Any, Tuple
from .rules_engine import RulesEngine, BANNED_AI_WORDS

# Replacement mapping for common AI phrases to plain human verbs
REPLACEMENT_MAP = {
    r"\butilize\b": "use",
    r"\butilizes\b": "uses",
    r"\butilized\b": "used",
    r"\butilizing\b": "using",
    r"\bfacilitate\b": "help",
    r"\bfacilitates\b": "helps",
    r"\bfacilitated\b": "helped",
    r"\bfacilitating\b": "helping",
    r"\bcommence\b": "start",
    r"\bcommences\b": "starts",
    r"\bcommenced\b": "started",
    r"\bshowcase\b": "show",
    r"\bshowcases\b": "shows",
    r"\bshowcased\b": "showed",
    r"\bshowcasing\b": "showing",
    r"\bobtain\b": "get",
    r"\bobtains\b": "gets",
    r"\bobtained\b": "got",
    r"\benhance\b": "improve",
    r"\benhances\b": "improves",
    r"\benhanced\b": "improved",
    r"\benhancing\b": "improving",
    r"\belucidate\b": "explain",
    r"\bascertain\b": "check",
    r"\bendeavor\b": "try",
    r"\bleverage\b": "use",
    r"\bleverages\b": "uses",
    r"\bleveraged\b": "used",
    r"\bleveraging\b": "using",
    r"\bharness\b": "use",
    r"\bharnesses\b": "uses",
    r"\bharnessed\b": "used",
    r"\bharnessing\b": "using",
    r"\bstreamline\b": "cut steps from",
    r"\bstreamlines\b": "cuts steps from",
    r"\bstreamlined\b": "simplified",
    r"\bfoster\b": "support",
    r"\bfosters\b": "supports",
    r"\bfostering\b": "supporting",
    r"\bpivotal\b": "central",
    r"\brobust\b": "tested",
    r"\bgroundbreaking\b": "new",
    r"\bgame-changer\b": "real shift",
    r"\bdeep dive\b": "close look",
    r"\binvaluable insights\b": "useful lessons",
    r"\bseamless\b": "direct",
    r"\bseamlessly\b": "directly",
    r"\bdelve into\b": "look closely at",
    r"\bdelves into\b": "looks closely at",
    r"\bdelving into\b": "looking closely at",
    r"\bdelved into\b": "looked closely at",
    r"\bdelve\b": "examine",
    r"\bdelves\b": "examines",
    r"\bdelving\b": "examining",
    r"\blandscape\b": "market",
    r"\btapestry\b": "mix",
    r"\bparadigm\b": "model",
    r"\bsynergies\b": "alignment",
    r"\bsynergy\b": "cooperation",
    r"\bmultifaceted\b": "varied",
    r"\bnuanced\b": "detailed",
    r"\btransformative\b": "major",
    r"\bcomprehensive\b": "full",
    r"\brevolutionary\b": "new",
    r"\binnovative\b": "new",
    r"\bcutting-edge\b": "modern"
}

class Humanizer:
    @staticmethod
    def humanize_text(text: str, mode: str = "strict") -> Tuple[str, Dict[str, Any]]:
        """
        4-Pass Humanizer Pipeline:
        Pass 1: SCRUB (Forensic + Strict replacements)
        Pass 2: RHYTHM (Normalize punctuation, em-dashes)
        Pass 3: REVEAL BRIDGES removal
        Pass 4: OVER-CORRECTION GUARD
        """
        cleaned = text
        changes_made = []

        # Pass 1: Replace AI buzzwords with plain human equivalents preserving sentence capitalization
        def _preserve_case_sub(pattern, replacement, text):
            def repl(match):
                matched_str = match.group(0)
                if matched_str.isupper() and len(matched_str) > 1:
                    return replacement.upper()
                elif matched_str[0].isupper():
                    return replacement[0].upper() + replacement[1:] if len(replacement) > 1 else replacement.upper()
                return replacement
            return re.subn(pattern, repl, text, flags=re.IGNORECASE)

        for pattern, replacement in REPLACEMENT_MAP.items():
            if re.search(pattern, cleaned, re.IGNORECASE):
                cleaned, count = _preserve_case_sub(pattern, replacement, cleaned)
                changes_made.append(f"Replaced AI buzzword with plain verb '{replacement}' ({count}x)")

        # Pass 2: Clean up generic openers & assistant preamble (including thinking chatter)
        lines = [l for l in cleaned.split('\n')]
        while lines and re.match(
            r'^(the user wants|here is a|sure,? here|okay,? here|let me check|let[\'’]?s write|post draft:?|draft:?|headline:?|thought:?|system:?)\b',
            lines[0].strip(),
            re.IGNORECASE
        ):
            removed_line = lines.pop(0)
            changes_made.append(f"Stripped assistant thought preamble: '{removed_line[:40]}...'")
        cleaned = '\n'.join(lines).strip()

        generic_intro_regex = r"^(in today['’]?s (rapidly evolving|digital|fast-paced|connected|modern) world,?|in the modern era,?|as technology continues to evolve,?)\s*"
        if re.search(generic_intro_regex, cleaned, re.IGNORECASE):
            cleaned = re.sub(generic_intro_regex, "", cleaned, flags=re.IGNORECASE)
            changes_made.append("Stripped generic intro filler")

        # Pass 3: Em-dash normalization (cap at max 1 per 100 words, replace extras with commas or parentheses)
        words = re.findall(r'\b\w+\b', cleaned)
        word_count = max(1, len(words))
        allowed_dashes = max(1, word_count // 100)

        dashes_found = list(re.finditer(r'—|--', cleaned))
        if len(dashes_found) > allowed_dashes:
            # Replace excess em dashes with commas or semicolons
            excess = len(dashes_found) - allowed_dashes
            for i in range(excess):
                cleaned = re.sub(r'(\w+)\s*(?:—|--)\s*(\w+)', r'\1, \2', cleaned, count=1)
            changes_made.append(f"Capped excess em-dashes (normalized {excess} to commas)")

        # Pass 4: Reveal bridges cleanup ("The result?", "Plot twist:")
        cleaned = re.sub(r'\b(the result\?|plot twist:|here[\'’]?s the thing:)\s*', '', cleaned, flags=re.IGNORECASE)

        # Audit the resulting text
        audit = RulesEngine.audit_text(cleaned)
        audit["changes_made"] = changes_made

        return cleaned, audit
