def truncate_text(text: str, max_chars: int) -> str:
    """
    Safely truncate text to a maximum length to prevent LLM token overflows.
    Appends a marker if truncation occurs.
    """
    if len(text) <= max_chars:
        return text

    # Keep the first (max_chars - 100) characters to reserve room for the marker
    truncated_len = max(0, max_chars - 100)
    return f"{text[:truncated_len]}... [truncated {len(text) - truncated_len} chars]"
