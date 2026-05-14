import pytest
from models.profile import Profile

def test_profile_creation():
    profile = Profile(
        name="TikTok",
        format="9:16",
        duration_min=15.0,
        duration_max=30.0,
        quantity=3,
        score_minimum=70
    )
    assert profile.name == "TikTok"
    assert profile.format == "9:16"

def test_profile_to_dict():
    profile = Profile(name="Test", format="16:9")
    data = profile.to_dict()
    assert data["name"] == "Test"

def test_profile_from_dict():
    data = {"name": "YouTube", "format": "16:9", "quantity": 5}
    profile = Profile.from_dict(data)
    assert profile.name == "YouTube"