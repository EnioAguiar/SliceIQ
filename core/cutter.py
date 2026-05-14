import ffmpeg
from pathlib import Path
from models.profile import Profile

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
        output_name: str = None
    ) -> Path:
        duration = end - start
        if duration < profile.duration_min:
            end = start + profile.duration_min
            duration = profile.duration_min
        elif duration > profile.duration_max:
            end = start + profile.duration_max
            duration = profile.duration_max

        input_path = Path(video_path)
        if output_name is None:
            output_name = f"{input_path.stem}_{profile.name}_{start:.0f}s.mp4"

        output_path = self.output_dir / output_name

        stream = ffmpeg.input(str(input_path), ss=start, t=duration)
        stream = ffmpeg.output(stream, str(output_path), vcodec="libx264", acodec="aac")
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        return output_path