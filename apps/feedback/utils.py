"""
Lightweight content moderation for anonymous feedback reviews.

This is a simple keyword-based filter meant for a college project scope.
Admins can extend BLOCKED_WORDS as needed. For production use, consider
a proper moderation API instead.
"""

BLOCKED_WORDS = {
    "stupid", "idiot", "useless", "hate", "shut up", "nonsense",
    "bakwas", "bekar", "faltu", "pagal",
}


def contains_abusive_language(text: str) -> bool:
    """Returns True if the text contains any blocked word (case-insensitive)."""
    if not text:
        return False
    lowered = text.lower()
    return any(word in lowered for word in BLOCKED_WORDS)
