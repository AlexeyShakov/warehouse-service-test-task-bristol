from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from dataclasses import asdict

from src.serializers import to_json
from src.infrastructure.mongo.connection import get_events_collection
from src.domains import (
    service as warehouse_monitor_service,
    exceptions as domain_exceptions,
)

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
    # TODO в данном словаре мы опираемся на реализацию Mongo, что неправильно для эндпоинта.
    # По-хорошему здесь должны быть универсальная структура, а вот на уровне репозитория, она бы подстраивалась под БД
    # Переделать, если хватит времени
    needed_fields = {
        "source": 1,
        "data.movement_id": 1,
        "data.warehouse_id": 1,
        "data.timestamp": 1,
        "data.quantity": 1,
        "data.event": 1,
    }
    sorting = (("data.timestamp", 1),)
    try:
        movement_info = await service.get_movement_info(
            movement_id, needed_fields, sorting
        )
    except domain_exceptions.MovementNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        # TODO добавить логгер
        raise HTTPException(status_code=500, detail="Unknown error")
    return to_json.MovementDiffInfoToJSON(**asdict(movement_info))
