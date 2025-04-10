from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection

from src.serializers import to_json
from src.infrastructure.mongo.connection import get_events_collection
from src.domains import (
    service as warehouse_monitor_service,
    exceptions as domain_exceptions,
)

warehouse_routes = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@warehouse_routes.get(
    "/{warehouse_id}/products/{product_id}",
    response_model=to_json.ProductQuantityToJSON,
    description="Возвращает информацию текущем запасе товара в конкретном складе",
)
async def get_product_info(
    warehouse_id: str,
    product_id: str,
    events_collection: AsyncIOMotorCollection = Depends(get_events_collection),
):
    service = await warehouse_monitor_service.get_service(events_collection)
    # TODO в данном словаре мы опираемся на реализацию Mongo, что неправильно для эндпоинта.
    # По-хорошему здесь должны быть универсальная структура, а вот на уровне репозитория, она бы подстраивалась под БД
    # Переделать, если хватит времени
    needed_fields = {"data.quantity": 1, "data.event": 1}
    try:
        remaining_product_quantity = await service.get_remaining_product_quantity(
            warehouse_id, product_id, needed_fields
        )
    except domain_exceptions.WarehouseOrProductNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        # TODO добавить логгер
        raise HTTPException(status_code=500, detail="Unknown error")
    return to_json.ProductQuantityToJSON(**{"quantity": remaining_product_quantity})
