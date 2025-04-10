from motor.motor_asyncio import AsyncIOMotorCollection
from src import type_hints, interfaces, models


class MongoRepo(interfaces.IWarehouseMonitorRepo):
    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    async def get_movement_info(
        self,
        needed_fields: type_hints.NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
        filtering_data: type_hints.FILTERING_DATA = None,
    ) -> list[models.MovementObj]:
        query = filtering_data or {}

        cursor = self._collection.find(query, projection=needed_fields or None)

        if order_by:
            cursor = cursor.sort(order_by)

        results: type_hints.MONGO_MOVEMENT_LIST = await cursor.to_list(length=None)
        return await self._deserialize_movement_data_objs(results)

    async def _deserialize_movement_data_objs(
        self, movement_docs: type_hints.MONGO_MOVEMENT_LIST
    ) -> list[models.MovementObj]:
        movements = []

        for doc in movement_docs:
            data = doc["data"]
            movement = models.MovementObj(
                movement_id=data["movement_id"],
                source=doc["source"],
                warehouse_id=data["warehouse_id"],
                timestamp=data["timestamp"],  # make it timezone-aware
                quantity=data["quantity"],
            )
            movements.append(movement)
        return movements

    async def get_remaining_product_info(
        self,
        filtering_data: dict[str, str],
        needed_fields: type_hints.NEEDED_FIELDS = None,
    ) -> list[models.RemainingProduct]:
        query = filtering_data or {}

        cursor = self._collection.find(query, projection=needed_fields or None)

        results: type_hints.REMAINING_PRODUCT_FROM_MONGO_LIST = await cursor.to_list(
            length=None
        )
        return await self._deserialize_remaining_products(results)

    async def _deserialize_remaining_products(
        self, remaining_products: type_hints.REMAINING_PRODUCT_FROM_MONGO_LIST
    ) -> list[models.RemainingProduct]:
        return [
            models.RemainingProduct(
                product["data"]["event"], product["data"]["quantity"]
            )
            for product in remaining_products
        ]
