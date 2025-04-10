from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

MOVEMENT_EVENTS = Literal["departure", "arrival"]


@dataclass(frozen=True)
class MovementObj:
    movement_id: str
    source: str
    warehouse_id: str
    timestamp: datetime
    quantity: int
    event: MOVEMENT_EVENTS


@dataclass(frozen=True)
class TimestampDiff:
    days: int
    hours: int
    minutes: int


@dataclass(frozen=True)
class MovementDiffInfo:
    movement_id: str
    quantity_diff: int
    source: Optional[str] = None
    destination: Optional[str] = None
    timestamp_diff: Optional[TimestampDiff] = None


@dataclass(frozen=True)
class RemainingProduct:
    event: MOVEMENT_EVENTS
    quantity: int
