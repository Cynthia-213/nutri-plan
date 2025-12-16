from pydantic import BaseModel
from typing import Optional

# --- Food Schema ---

# Base properties for a food item
class FoodBase(BaseModel):
    description: str
    category: Optional[str] = None
    energy_kcal: float
    protein_g: float
    fat_g: float
    carbohydrate_g: float
    serving_size_g: Optional[float] = 100.0

# Properties to return to the client
class Food(FoodBase):
    id: int
    fdc_id: Optional[int] = None

    class Config:
        from_attributes = True
