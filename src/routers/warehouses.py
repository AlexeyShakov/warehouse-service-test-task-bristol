from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from src.serializers import to_json
from src.infrastructure.db import get_events_collection
from src import service as warehouse_monitor_service

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
    needed_fields = {"data.quantity": 1, "event": 1}
    remaining_product_quantity = await service.get_remaining_product_quantity(
        warehouse_id, product_id, needed_fields
    )
    return to_json.ProductQuantityToJSON(**{"quantity": remaining_product_quantity})
