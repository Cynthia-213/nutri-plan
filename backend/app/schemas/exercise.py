from pydantic import BaseModel
from typing import Optional

# --- Exercise Schema ---

# Base properties for an exercise
class ExerciseBase(BaseModel):
    name: str
    met_value: float
    description: Optional[str] = None

# Properties to return to the client
class Exercise(ExerciseBase):
    id: int

    class Config:
        from_attributes = True
