from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi_cache.decorator import cache
from src.config import get_project_settings

from src.serializers import to_json
from src.infrastructure.mongo.connection import get_events_collection
from src.infrastructure import logger
from src.domains import (
    service as warehouse_monitor_service,
    exceptions as domain_exceptions,
)
from pydantic import BaseModel

SETTINGS = get_project_settings()
warehouse_routes = APIRouter(prefix="/warehouses", tags=["Warehouses"])


class ErrorResponse(BaseModel):
    detail: str


@warehouse_routes.get(
    "/{warehouse_id}/products/{product_id}",
    response_model=to_json.ProductQuantityToJSON,
    description="Возвращает информацию текущем запасе товара в конкретном складе",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Warehouse or product are not found",
        },
        500: {"model": ErrorResponse, "description": "Unknown server error"},
    },
)
@cache(expire=SETTINGS.ttl)
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
        logger.LOGGER.exception(f"Неизвестная ошибка при получении информации о товаре с id {product_id}\
        на складе с id {warehouse_id}")
        raise HTTPException(status_code=500, detail="Unknown error")
    return to_json.ProductQuantityToJSON(**{"quantity": remaining_product_quantity})
