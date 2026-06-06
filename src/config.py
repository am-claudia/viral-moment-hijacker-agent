import os

ORCHESTRATOR_MODEL = "claude-opus-4-8"

def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set.\n"
            "Copy .env.example to .env and add your key from console.anthropic.com"
        )
    return key
