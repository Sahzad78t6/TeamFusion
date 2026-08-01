"""Tools for the Supervisor Agent."""
import os
from app.llm.provider import llm_provider

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.md")
SYSTEM = open(PROMPT_PATH).read() if os.path.exists(PROMPT_PATH) else ""

# The router logic is in router.py. This file is kept for structural consistency.
