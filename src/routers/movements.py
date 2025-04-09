from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from dataclasses import asdict

from src.serializers import to_json
from src.infrastructure.db import get_events_collection
from src import service as warehouse_monitor_service


movements_routes = APIRouter(prefix="/movements", tags=["Movements"])


@movements_routes.get(
    "/{movement_id}",
    response_model=to_json.MovementDiffInfoToJSON,
    description="Возвращает информацию о перемещении по его ID",
)
async def get_movement_info(
    movement_id: str,
    events_collection: AsyncIOMotorCollection = Depends(get_events_collection),
):
    service = await warehouse_monitor_service.get_service(events_collection)
    needed_fields = {
        "source": 1,
        "data.movement_id": 1,
        "data.warehouse_id": 1,
        "data.timestamp": 1,
        "data.quantity": 1,
    }
    sorting = (("data.timestamp", 1),)
    movement_info = await service.get_movement_info(movement_id, needed_fields, sorting)
    return to_json.MovementDiffInfoToJSON(**asdict(movement_info))
