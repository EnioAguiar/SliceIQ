from typing import Literal
from pydantic import BaseModel

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
        response = self._call_llm(prompt)
        return self._parse_response(response)

    def _build_prompt(self, text: str, quantity: int, min_dur: float, max_dur: float) -> str:
        return f"""Analise este transcript de vídeo e identifique os {quantity} melhores highlights.
Duração desejada: {min_dur}s a {max_dur}s por highlight.

Transcript:
{text}

Retorne em formato JSON:
{{"highlights": [
  {{"start": 0.0, "end": 30.0, "score": 85, "reason": "explicação do momento"}}
]}}"""

    def _call_llm(self, prompt: str) -> str:
        if self.provider == "mock":
            return self._mock_response()
        elif self.provider == "minimax":
            return self._call_minimax(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        return self._call_ollama(prompt)

    def _call_minimax(self, prompt: str) -> str:
        from config.llm_config import LLMConfig
        import requests

        if not LLMConfig.MINIMAX_API_KEY:
            return self._mock_response()

        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {LLMConfig.MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "minimax-01",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["choices"][0]["message"]["content"]

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

    def _mock_response(self) -> str:
        import json
        return json.dumps({
            "highlights": [
                {"start": 0.0, "end": 30.0, "score": 80, "reason": "mock highlight"},
                {"start": 45.0, "end": 75.0, "score": 75, "reason": "mock highlight 2"}
            ]
        })

    def _parse_response(self, response: str) -> list[Highlight]:
        import json, re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return [Highlight(**h) for h in data.get("highlights", [])]
        return []