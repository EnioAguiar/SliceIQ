import ffmpeg
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Cutter:
    ASPECT_RATIOS = {
        "9:16": "9/16",
        "1:1": "1/1",
        "16:9": "16/9",
        "4:3": "4/3"
    }

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def cut_video(
        self,
        video_path: str,
        start: float,
        end: float,
        profile: Profile,
        index: int = 0,
        output_name: str = None,
        strict_duration: bool = False
    ) -> Path:
        duration = end - start
        if strict_duration:
            if duration < profile.duration_min:
                raise ValueError(
                    f"Duration {duration:.1f}s is below minimum {profile.duration_min}s. "
                    f"Workflow should re-evaluate this highlight."
                )
            if duration > profile.duration_max:
                raise ValueError(
                    f"Duration {duration:.1f}s exceeds maximum {profile.duration_max}s. "
                    f"Workflow should re-evaluate this highlight."
                )

        input_path = Path(video_path)
        if output_name is None:
            output_name = f"{input_path.stem}_{profile.name}_{index+1:03d}.mp4"

        output_path = self.output_dir / output_name

        logger.info(f"Cutting {start:.1f}s - {end:.1f}s (duration: {duration:.1f}s)...")

        stream = ffmpeg.input(str(input_path), ss=start, t=duration)
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vcodec="libx264",
            acodec="aac",
            preset="fast",
            crf=23,
           threads=4
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=False, capture_stdout=True, capture_stderr=True)

        logger.info(f"Saved: {output_path.name}")
        return output_path