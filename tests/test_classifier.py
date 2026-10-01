import pytest

from app.domain.services.breaking_change_classifier import BreakingChangeClassifier


@pytest.mark.parametrize(
    ("title", "summary", "expected"),
    [
        ("Removed the client_id field", "", True),
        ("v2.0 Breaking changes", "", True),
        ("Deprecating the /v1/charges endpoint", "", True),
        ("Dropped support for Python 3.8", "", True),
        ("Renamed `plan` to `price`", "", True),
        ("Improved error messages", "", False),
        ("Add new webhook event", "", False),
        ("v1.2.3", '<p>See <a href="https://x/removed-docs">the changelog</a></p>', False),
        ("v3", "<ul><li>No breaking changes</li><li>Non-breaking fix</li></ul>", False),
        ("v3", "<ul><li>Remove inequality examples from filter descriptions</li></ul>", False),
        ("v3", "<ul><li>Fix</li><li><b>Remove</b> <code>&lt;Assistant&gt;</code> noun</li></ul>", True),
        ("v4", "<p>⚠️ Remove support for execute</p>", True),
        ("v4", "<p>Updated a prose reference to the renamed op</p>", False),
    ],
)
def test_is_breaking(title: str, summary: str, expected: bool) -> None:
    assert BreakingChangeClassifier().is_breaking(title, summary) is expected
