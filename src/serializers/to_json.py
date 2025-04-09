from pydantic import BaseModel
from typing import Optional


class TimestampDiffSchema(BaseModel):
    days: int
    hours: int
    minutes: int


class MovementDiffInfoToJSON(BaseModel):
    movement_id: str
    quantity_diff: int
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_diff: Optional[TimestampDiffSchema] = None


class ProductQuantityToJSON(BaseModel):
    quantity: int
