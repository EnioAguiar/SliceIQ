from faster_whisper import WhisperModel
import torch

class Transcript:
    MODELS = ["tiny", "base", "small", "medium", "large-v3"]

    def __init__(self, model_size: str = "medium", device: str = "cuda"):
        self.model_size = model_size
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = None

    @staticmethod
    def get_available_models() -> list:
        return Transcript.MODELS

    def load_model(self):
        compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=compute_type
        )

    def transcribe(self, video_path: str, language: str = "pt") -> list:
        if self.model is None:
            self.load_model()

        segments, _ = self.model.transcribe(
            video_path,
            language=language,
            vad_filter=True
        )

        return [
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            }
            for seg in segments
        ]

    def get_full_text(self, video_path: str, language: str = "pt") -> str:
        segments = self.transcribe(video_path, language)
        return " ".join(s["text"] for s in segments)