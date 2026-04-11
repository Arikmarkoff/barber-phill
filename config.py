import os

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

# LLM provider: "openai" (RouterAI совместим с OpenAI API)
LLM_PROVIDER = "openai"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-opus-4-6"

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = "anthropic/claude-sonnet-4.6"
OPENAI_BASE_URL = "https://routerai.ru/api/v1"
