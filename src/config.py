import os

# Orchestrator: full reasoning power for strategy, angle selection, and DM writing
ORCHESTRATOR_MODEL = "claude-opus-4-8"

# Sub-agents: fast and cheap for structured data analysis tasks
TREND_AGENT_MODEL = "claude-haiku-4-5-20251001"
INFLUENCER_AGENT_MODEL = "claude-haiku-4-5-20251001"

# Sub-agent: Sonnet for creative email copywriting — better quality than Haiku
EMAIL_AGENT_MODEL = "claude-sonnet-4-6"


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set.\n"
            "Copy .env.example to .env and add your key from console.anthropic.com"
        )
    return key
