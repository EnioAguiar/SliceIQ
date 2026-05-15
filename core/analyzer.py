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

    def _sample_transcript(self, segments: list, max_chars: int = 50000) -> str:
        result = []
        total_chars = 0
        for seg in segments:
            text = f"[{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}"
            if total_chars + len(text) > max_chars:
                break
            result.append(text)
            total_chars += len(text)
        return "\n".join(result)

    def _build_prompt(self, text: str, quantity: int, min_dur: float, max_dur: float) -> str:
        import json
        from pathlib import Path
        transcript_file = Path("transcript_debug.json")
        if transcript_file.exists():
            with open(transcript_file, "r") as f:
                data = json.load(f)
                segments_text = self._sample_transcript(data["segments"], max_chars=50000)
                long_segments = [
                    s for s in data["segments"]
                    if (s["end"] - s["start"]) >= min_dur
                ]
                long_segments.sort(key=lambda s: s["end"] - s["start"], reverse=True)
                examples_text = ""
                for i, seg in enumerate(long_segments[:3]):
                    duration = seg["end"] - seg["start"]
                    examples_text += f'\nExample: {{"start": {seg["start"]:.1f}, "end": {seg["end"]:.1f}, "score": 85, "reason": "momento relevante com {duration:.0f}s"}}'
        else:
            segments_text = text
            examples_text = ""

        return f"""Analise este transcript de vídeo e identifique os {quantity} melhores highlights.
        Duração desejada: {min_dur}s a {max_dur}s por highlight.
        Cada highlight deve ter timestamps de INÍCIO e FIM que sejam momentos distintos no vídeo (não consecutivos).
        Timestamps devem ser em SEGUNDOS EXATOS com 1 casa decimal (ex: 125.5, não 125 ou 125.567).
        {examples_text}

        Transcript com timestamps:
        {segments_text}

        Raciocínio: Analisando transcript para momentos com alto potencial de destaque. Estou procurando:
        1. Momentos com hook forte (pergunta, declaração impactante)
        2. Trechos com informação densa ou citação marcante
        3. Momentos que respeitem o range de {min_dur}s a {max_dur}s
        Antes de responder, verificar se cada highlight está dentro do range permitido.

        → Highlights (JSON):
        {{"highlights": [
          {{"start": 0.0, "end": 0.0, "score": 0, "reason": "..."}}
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
            },
            timeout=120
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
            highlights_data = data.get("candidates") or data.get("highlights") or []
            return [Highlight(**h) for h in highlights_data]
        return []