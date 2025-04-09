from pydantic import BaseModel
from typing import Literal
from uuid import UUID
from datetime import datetime


class WarehouseEventData(BaseModel):
    movement_id: UUID
    warehouse_id: UUID
    timestamp: datetime
    event: Literal["arrival", "departure"]
    product_id: UUID
    quantity: int


class WarehouseEvent(BaseModel):
    id: UUID
    source: str
    specversion: str
    type: Literal["ru.retail.warehouses.movement"]
    datacontenttype: Literal["application/json"]
    dataschema: str
    time: int
    subject: str
    destination: str
    data: WarehouseEventData
