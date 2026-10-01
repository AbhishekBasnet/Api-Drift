import re

BREAKING_PATTERNS = [
    r"\bbreaking\b",
    r"\bremov(?:e|ed|es|al)\b",
    r"\bdeprecat\w*",
    r"\bno longer\b",
    r"\brenam(?:e|ed|es)\b",
    r"\bdrop(?:s|ped)? support\b",
    r"\bincompatible\b",
    r"\bend[- ]of[- ]life\b",
    r"\bsunset\w*",
    r"\bdiscontinu\w*",
]

BREAKING_REGEX = re.compile("|".join(BREAKING_PATTERNS), re.IGNORECASE)
HTML_TAG_REGEX = re.compile(r"<[^>]+>")


class BreakingChangeClassifier:
    def is_breaking(self, title: str, summary: str) -> bool:
        text = HTML_TAG_REGEX.sub(" ", f"{title} {summary}")
        return BREAKING_REGEX.search(text) is not None
