from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from src.domains import models


class WarehouseEventData(BaseModel):
    movement_id: str
    warehouse_id: str
    timestamp: datetime
    event: models.MOVEMENT_EVENTS
    product_id: str
    quantity: int


class WarehouseEvent(BaseModel):
    id: str
    source: str
    specversion: str
    type: Literal["ru.retail.warehouses.movement"]
    datacontenttype: Literal["application/json"]
    dataschema: str
    time: int
    subject: str
    destination: str
    data: WarehouseEventData
