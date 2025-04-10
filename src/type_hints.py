from datetime import datetime
from typing import List, TypedDict, Optional, Literal, Sequence, Any
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

NEEDED_FIELDS = Optional[dict[str, Literal[0, 1]]]
ORDER_BY = Optional[Sequence[tuple[str, int]]]
FILTERING_DATA = Optional[dict[str, Any]]


class PartialMovementData(TypedDict):
    event: Literal["arrival", "departure"]
    quantity: int


class RemainingProductDoc(TypedDict):
    _id: ObjectId
    data: PartialMovementData


REMAINING_PRODUCT_FROM_MONGO_LIST = list[RemainingProductDoc]
