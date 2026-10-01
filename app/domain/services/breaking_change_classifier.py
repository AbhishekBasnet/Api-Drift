import html
import re

EXPLICIT_REGEX = re.compile(r"(?<!no )(?<!non-)(?<!non )\bbreaking\b|⚠", re.IGNORECASE)

KEYWORD_REGEX = re.compile(
    r"\bremov(?:e|ed|es|al)\b"
    r"|\bdeprecat\w*"
    r"|\bno longer\b"
    r"|\brenam(?:e|ed|es)\b"
    r"|\bdrop(?:s|ped)? support\b"
    r"|\bincompatible\b"
    r"|\bend[- ]of[- ]life\b"
    r"|\bsunset\w*"
    r"|\bdiscontinu\w*",
    re.IGNORECASE,
)

DOCS_ONLY_REGEX = re.compile(
    r"\b(?:descriptions?|examples?|docs?|documentation|typos?|prose|comments?|readme|mdx|tests?|workflows?)\b",
    re.IGNORECASE,
)

BLOCK_TAG_REGEX = re.compile(r"</?(?:p|li|ul|ol|br|h\d|div)\b[^>]*>", re.IGNORECASE)
TAG_REGEX = re.compile(r"<[^>]+>")


class BreakingChangeClassifier:
    def is_breaking(self, title: str, summary: str) -> bool:
        return any(self._is_breaking_line(line) for line in self._split_lines(title, summary))

    @staticmethod
    def _split_lines(title: str, summary: str) -> list[str]:
        text = BLOCK_TAG_REGEX.sub("\n", f"{title}\n{summary}")
        text = html.unescape(TAG_REGEX.sub(" ", text))
        return [line.strip() for line in text.splitlines() if line.strip()]

    @staticmethod
    def _is_breaking_line(line: str) -> bool:
        if EXPLICIT_REGEX.search(line):
            return True
        return KEYWORD_REGEX.search(line) is not None and DOCS_ONLY_REGEX.search(line) is None
