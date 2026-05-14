from pathlib import Path

class Settings:
    PROJECT_ROOT = Path(__file__).parent.parent
    PROFILES_DIR = PROJECT_ROOT / "profiles"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    DEFAULT_MODEL = "medium"
    CUDA_DEVICE = 0

settings = Settings()