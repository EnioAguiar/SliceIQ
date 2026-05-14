from pathlib import Path
import os

class Settings:
    PROJECT_ROOT = Path(__file__).parent.parent
    PROFILES_DIR = PROJECT_ROOT / "profiles"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    DEFAULT_MODEL = "medium"
    CUDA_DEVICE = 0
    MINIMAX_MODE = os.getenv("MINIMAX_MODE", "paygo")

settings = Settings()