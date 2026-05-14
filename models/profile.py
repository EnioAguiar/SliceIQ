from pydantic import BaseModel
from typing import Literal

class Profile(BaseModel):
    name: str
    format: Literal["9:16", "1:1", "16:9", "4:3"]
    duration_min: float = 15.0
    duration_max: float = 60.0
    quantity: int = 5
    score_minimum: int = 60
    tipo: Literal["short", "medio", "normal"] = "medio"
    face_crop: bool = False

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        return cls(**data)