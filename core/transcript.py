from faster_whisper import WhisperModel
import torch
import subprocess
import os
import tempfile
import json
import logging

logger = logging.getLogger(__name__)


class Transcript:
    MODELS = ["tiny", "base", "small", "medium", "large-v3"]

    def __init__(self, model_size: str = "medium", device: str = "cpu"):
        self.model_size = model_size
        self.device = device
        self.model = None

    @staticmethod
    def get_available_models() -> list:
        return Transcript.MODELS

    def load_model(self):
        self.model = WhisperModel(
            self.model_size,
            device="cpu",
            compute_type="int8"
        )

    def _convert_video_to_wav(self, video_path: str) -> str:
        wav_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-ar', '16000', '-ac', '1', '-acodec', 'pcm_s16le',
            wav_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return wav_path

    def transcribe(self, video_path: str, language: str = "pt") -> list:
        if self.model is None:
            self.load_model()

        wav_path = self._convert_video_to_wav(video_path)
        try:
            segments, _ = self.model.transcribe(
                wav_path,
                language=language,
                vad_filter=True
            )
            result = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip()
                }
                for seg in segments
            ]
            self._save_transcript(result, video_path)
            return result
        finally:
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def _save_transcript(self, segments: list, video_path: str):
        data = {
            "segments": segments,
            "full_text": " ".join(s["text"] for s in segments)
        }
        with open("transcript_debug.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Transcript saved: {len(segments)} segments")

    def get_full_text(self, video_path: str, language: str = "pt") -> str:
        segments = self.transcribe(video_path, language)
        return " ".join(s["text"] for s in segments)