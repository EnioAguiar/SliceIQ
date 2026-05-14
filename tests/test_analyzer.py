import pytest
from core.analyzer import Analyzer, Highlight

def test_analyzer_initialization():
    a = Analyzer(provider="minimax")
    assert a.provider == "minimax"

def test_mock_response():
    a = Analyzer(provider="mock")
    highlights = a.extract_highlights("texto de teste", quantity=3)
    assert len(highlights) <= 3
    assert all(isinstance(h, Highlight) for h in highlights)

def test_extract_highlights_returns_list():
    a = Analyzer(provider="mock")
    highlights = a.extract_highlights("texto de teste", quantity=5)
    assert isinstance(highlights, list)

def test_highlight_model():
    h = Highlight(start=0.0, end=30.0, score=85, reason="test")
    assert h.start == 0.0
    assert h.score == 85