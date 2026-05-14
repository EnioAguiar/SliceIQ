import os

class LLMConfig:
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_PROVIDER = "minimax"

    PROVIDERS = ["minimax", "gemini", "ollama"]