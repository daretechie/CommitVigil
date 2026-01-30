# Copyright (c) 2026 CommitVigil AI. All rights reserved.
import re


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


# Known prompt injection patterns to detect and neutralize
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions|rules)",
    r"forget\s+(everything|all)\s+(above|before)",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"</\s*system\s*>",
    r"\[INST\]",
    r"\[/INST\]",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def sanitize_prompt_input(text: str) -> str:
    """
    Sanitize user input to mitigate LLM prompt injection attacks.
    
    Strategy:
    1. Detect and flag known injection patterns.
    2. Escape XML-like control sequences recursively that could break prompt structure.
    3. Normalize whitespace and remove hidden control characters.
    4. [ADVERSARIAL] Multi-layered filtering of sensitive keywords.
    """
    if not text:
        return ""
    
    # 0. Strip hidden control characters (prevent bypasses using \x00, etc.)
    sanitized = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    
    # 1. Detect and neutralize known injection patterns
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(sanitized):
            sanitized = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", sanitized)
    
    # 2. Escape standalone angle brackets recursively (handles <<TAG>>)
    # and fragmented tags
    loop_limit = 5
    while ("<" in sanitized or ">" in sanitized) and loop_limit > 0:
        prev = sanitized
        sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;")
        if prev == sanitized:
            break
        loop_limit -= 1
    
    # 3. Restore ONLY our expected prompt XML tags (Strict Whitelist)
    known_tags = [
        "user_excuse", "user_input", "historical_context", "current_status",
        "conversation_log", "promised_tasks", "actual_work_done", 
        "human_claims", "technical_evidence"
    ]
    for tag in known_tags:
        # Search for for escaped versions and restore
        sanitized = sanitized.replace(f"&lt;{tag}&gt;", f"<{tag}>")
        sanitized = sanitized.replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    
    # 4. Final safety check for un-matched or dangling brackets
    if "&lt;" in sanitized and "&gt;" not in sanitized:
        sanitized = sanitized.replace("&lt;", "[UNMATCHED_TAG]")

    # 5. Normalize excessive whitespace
    sanitized = re.sub(r"\s{3,}", "  ", sanitized)
    
    return sanitized.strip()

