from pydantic import BaseModel

class Profile(BaseModel):
    name: str
    format: str
    duration_min: float = 15.0
    duration_max: float = 900.0
    quantity: int = 5
    score_minimum: int = 60
    face_crop: bool = False

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        return cls(**data)