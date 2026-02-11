from pydantic import BaseModel


class CharacterOut(BaseModel):
    id: str
    name: str
    avatar_url: str | None = None
    tone: str
    dominance: float
    affection: float
    explicit_level: float
    boundaries: list[str]

    class Config:
        from_attributes = True