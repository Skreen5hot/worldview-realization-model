"""Credential presence check only (no generation code lives in E2; the LLM Gate B is E3)."""
import os


def available() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    try:
        import anthropic
        c = anthropic.Anthropic()
        return bool(getattr(c, "api_key", None) or getattr(c, "auth_token", None))
    except Exception:
        return False
