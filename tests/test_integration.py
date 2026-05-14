import pytest
from pathlib import Path
from models.profile import Profile
from core import VideoProcessor, Transcript, Analyzer, Cutter

@pytest.fixture
def sample_video():
    return "tests/fixtures/sample.mp4"

@pytest.fixture
def sample_profile():
    return Profile(
        name="Test",
        format="16:9",
        duration_min=10.0,
        duration_max=30.0,
        quantity=2,
        score_minimum=50
    )

def test_full_pipeline(sample_video, sample_profile):
    if not Path(sample_video).exists():
        pytest.skip("No sample video")

    processor = VideoProcessor()
    info = processor.get_video_info(sample_video)
    assert info["duration"] > 0

    transcript = Transcript()
    text = transcript.get_full_text(sample_video)
    assert len(text) > 0

    analyzer = Analyzer(provider="mock")
    highlights = analyzer.extract_highlights(text, quantity=2)
    assert len(highlights) <= 2

    cutter = Cutter(output_dir="tests/output")
    for h in highlights:
        path = cutter.cut_video(sample_video, h.start, h.end, sample_profile)
        assert path.exists()