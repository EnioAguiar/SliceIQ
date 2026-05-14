# core/title_generator.py
import logging
import random
from typing import Literal

logger = logging.getLogger(__name__)

TEMPLATES = {
    "chamativo": [
        "BREAKING:",
        "ISSO VAI EXPLODIR:",
        "VOCÊ NÃO VAI ACREDITAR:"
    ],
    "informativo": [
        "EXPLICADO:",
        "O QUE ACONTECEU:",
        "RESUMO:"
    ],
    "provocativo": [
        "SERÁ QUE:",
        "CUIDADO:",
        "ATENÇÃO:"
    ],
    "questionador": [
        "POR QUEM?",
        "COMO ASSIM?",
        "O QUE ISSO SIGNIFICA?"
    ]
}

VARIABLES = ["{text}", "{start}", "{end}", "{duration}"]

class TitleGenerator:
    MODES = ["auto", "template", "custom"]

    def __init__(self, mode: Literal["auto", "template", "custom"], config: dict):
        if mode not in self.MODES:
            raise ValueError(f"Mode must be one of {self.MODES}")
        self.mode = mode
        self.config = config

    def generate_title(
        self,
        highlight_text: str,
        start: float,
        end: float,
        duration: float
    ) -> str:
        if self.mode == "auto":
            return self._generate_auto(highlight_text, duration)
        elif self.mode == "template":
            return self._generate_template(highlight_text)
        elif self.mode == "custom":
            return self._generate_custom(highlight_text, start, end, duration)

    def _generate_auto(self, text: str, duration: float) -> str:
        prompt = f"""Analise este trecho de vídeo e gere um título chamativo e descritivo.
Trecho: {text}
Duração: {duration:.0f}s

Retorne apenas o título em português, até 50 caracteres, sem aspas."""

        response = self._call_minimax(prompt)
        return response[:50].strip()

    def _generate_template(self, text: str) -> str:
        selected = self.config.get("templates", [])
        prefixes = []
        for cat in selected:
            if cat in TEMPLATES and TEMPLATES[cat]:
                prefixes.append(random.choice(TEMPLATES[cat]))

        prompt = f"""Gere um título para este trecho de vídeo.
Combine os estilos: {', '.join(selected)}
Trecho: {text}

Retorne apenas o título em português, até 50 caracteres, sem aspas."""

        title = self._call_minimax(prompt)
        if prefixes:
            prefix = random.choice(prefixes)
            title = f"{prefix} {title}"
        return title[:50].strip()

    def _generate_custom(self, text: str, start: float, end: float, duration: float) -> str:
        template = self.config.get("prompt", "{text}")
        filled = template.replace("{text}", text)
        filled = filled.replace("{start}", f"{start:.1f}")
        filled = filled.replace("{end}", f"{end:.1f}")
        filled = filled.replace("{duration}", f"{duration:.1f}")

        prompt = f"""Com base neste contexto, gere um título para trecho de vídeo.
Contexto: {filled}

Retorne apenas o título em português, até 50 caracteres, sem aspas."""

        return self._call_minimax(prompt)[:50].strip()

    def _call_minimax(self, prompt: str) -> str:
        from config.llm_config import LLMConfig
        import requests

        if not LLMConfig.MINIMAX_API_KEY:
            logger.warning("No Minimax API key, returning placeholder title")
            return "titulo_generico"

        from config.settings import settings
        is_token_plan = getattr(settings, 'MINIMAX_MODE', 'paygo') == 'token_plan'

        if is_token_plan:
            url = "https://api.minimax.io/anthropic/v1/messages"
            model = "MiniMax-M2.7"
        else:
            url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
            model = "minimax-01"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {LLMConfig.MINIMAX_API_KEY}",
                "Content-Type": "application/json",
                "x-api-key": LLMConfig.MINIMAX_API_KEY
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = response.json()

        if is_token_plan:
            content = data.get("content", [])
            for block in content:
                if block.get("type") == "text":
                    return block.get("text", "").strip()
            return ""
        else:
            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()