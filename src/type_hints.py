from datetime import datetime
from typing import List, TypedDict, Optional, Literal, Sequence
from bson import ObjectId


class MovementDataDict(TypedDict):
    movement_id: str
    warehouse_id: str
    timestamp: datetime
    quantity: int


class MongoMovementDocument(TypedDict):
    _id: ObjectId
    source: str
    data: MovementDataDict


MONGO_MOVEMENT_LIST = List[MongoMovementDocument]

MOVEMENT_NEEDED_FIELDS = Optional[dict[str, Literal[0, 1]]]
ORDER_BY = Optional[Sequence[tuple[str, int]]]
