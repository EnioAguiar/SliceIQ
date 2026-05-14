from typing import Literal
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class Highlight(BaseModel):
    start: float
    end: float
    score: int
    reason: str

class Analyzer:
    def __init__(self, provider: Literal["minimax", "gemini", "ollama"] = "minimax"):
        self.provider = provider

    def extract_highlights(
        self,
        transcript_text: str,
        quantity: int = 5,
        duration_min: float = 15.0,
        duration_max: float = 60.0
    ) -> list[Highlight]:
        prompt = self._build_prompt(transcript_text, quantity, duration_min, duration_max)
        response = self._call_llm(prompt, quantity)
        return self._parse_response(response)

    def _build_prompt(self, text: str, quantity: int, min_dur: float, max_dur: float) -> str:
        import json
        from pathlib import Path
        transcript_file = Path("transcript_debug.json")
        if transcript_file.exists():
            with open(transcript_file, "r") as f:
                data = json.load(f)
                segments_text = "\n".join([
                    f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}"
                    for s in data["segments"]
                ])
        else:
            segments_text = text

        return f"""Analise este transcript de vídeo e identifique os {quantity} melhores highlights.
Duração desejada: {min_dur}s a {max_dur}s por highlight.
Cada highlight deve ter timestamps de INÍCIO e FIM que sejam momentos distintos no vídeo (não consecutivos).

Transcript com timestamps:
{segments_text}

Retorne em formato JSON:
{{"highlights": [
  {{"start": 0.0, "end": 30.0, "score": 85, "reason": "explicação do momento"}}
]}}"""

    def _call_llm(self, prompt: str, quantity: int = 5) -> str:
        if self.provider == "mock":
            return self._mock_response(quantity)
        elif self.provider == "minimax":
            return self._call_minimax(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        return self._call_ollama(prompt)

    def _call_minimax(self, prompt: str, quantity: int = 5) -> str:
        from config.llm_config import LLMConfig
        import requests

        if not LLMConfig.MINIMAX_API_KEY:
            return self._mock_response(quantity)

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
        logger.info(f"Minimax response: {response.json()}")
        data = response.json()

        if is_token_plan:
            content = data.get("content", [])
            text_result = ""
            for block in content:
                if block.get("type") == "text":
                    text_result = block.get("text", "")
                    break
            if not text_result and content:
                text_result = content[-1].get("text", "") if len(content) > 1 else ""
            return text_result
        else:
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _call_gemini(self, prompt: str) -> str:
        from config.llm_config import LLMConfig
        import requests

        if not LLMConfig.GEMINI_API_KEY:
            return self._mock_response()

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={LLMConfig.GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _call_ollama(self, prompt: str) -> str:
        import requests
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": "llama3", "messages": [{"role": "user", "content": prompt}]}
        )
        return response.json()["message"]["content"]

    def _mock_response(self, quantity: int = 5) -> str:
        import json, random
        highlights = []
        for i in range(quantity):
            start = random.uniform(60, 1200)
            end = start + random.uniform(20, 50)
            highlights.append({
                "start": round(start, 1),
                "end": round(end, 1),
                "score": random.randint(70, 95),
                "reason": f"mock highlight {i+1}"
            })
        return json.dumps({"highlights": highlights})

    def _parse_response(self, response: str) -> list[Highlight]:
        import json, re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return [Highlight(**h) for h in data.get("highlights", [])]
        return []