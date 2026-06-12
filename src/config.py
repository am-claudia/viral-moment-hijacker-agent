import os

# Orchestrator: strategy, angle selection, DM writing
ORCHESTRATOR_MODEL = "gemini-2.5-flash"

# Sub-agents: trend analysis and influencer scoring
TREND_AGENT_MODEL = "gemini-2.5-flash"
INFLUENCER_AGENT_MODEL = "gemini-2.5-flash"

# Sub-agent: customer email copywriting
EMAIL_AGENT_MODEL = "gemini-2.5-flash"


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY not set.\n"
            "Copy .env.example to .env and add your key from aistudio.google.com"
        )
    return key
