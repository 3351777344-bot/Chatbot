"""Conversation title generation helpers."""


def generate_fallback_title(first_message: str, max_length: int = 24) -> str:
    """Generate a simple local title from the first user message."""
    text = " ".join(first_message.strip().split())
    if not text:
        return "New conversation"
    return text[:max_length] + ("..." if len(text) > max_length else "")
