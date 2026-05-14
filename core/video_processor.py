import ffmpeg
from pathlib import Path

class VideoProcessor:
    SUPPORTED_FORMATS = ["mp4", "mkv", "avi", "mov", "webm"]

    def __init__(self):
        pass

    def get_video_info(self, video_path: str) -> dict:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        probe = ffmpeg.probe(str(path))
        video_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "video"),
            None
        )
        audio_stream = next(
            (s for s in probe["streams"] if s["codec_type"] == "audio"),
            None
        )

        return {
            "duration": float(probe["format"]["duration"]),
            "width": int(video_stream["width"]) if video_stream else 0,
            "height": int(video_stream["height"]) if video_stream else 0,
            "codec": video_stream["codec_name"] if video_stream else None,
            "fps": eval(video_stream["r_frame_rate"]) if video_stream else 0,
            "has_audio": audio_stream is not None
        }

    def is_valid_video(self, video_path: str) -> bool:
        path = Path(video_path)
        return path.suffix.lstrip(".") in self.SUPPORTED_FORMATS