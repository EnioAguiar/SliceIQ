import pytest
from pathlib import Path
from core.video_processor import VideoProcessor

@pytest.fixture
def processor():
    return VideoProcessor()

def test_supported_formats(processor):
    assert "mp4" in processor.SUPPORTED_FORMATS
    assert "mkv" in processor.SUPPORTED_FORMATS
    assert "avi" in processor.SUPPORTED_FORMATS
    assert "mov" in processor.SUPPORTED_FORMATS
    assert "webm" in processor.SUPPORTED_FORMATS

def test_is_valid_video(processor):
    assert processor.is_valid_video("video.mp4") == True
    assert processor.is_valid_video("video.mkv") == True
    assert processor.is_valid_video("video.txt") == False

def test_get_video_info_missing_file(processor):
    with pytest.raises(FileNotFoundError):
        processor.get_video_info("nonexistent.mp4")

@pytest.fixture
def sample_video():
    return Path("tests/fixtures/sample.mp4")

def test_get_video_info_with_fixture(sample_video):
    if not sample_video.exists():
        pytest.skip("No sample video")
    processor = VideoProcessor()
    info = processor.get_video_info(str(sample_video))
    assert "duration" in info
    assert "width" in info
    assert "height" in info