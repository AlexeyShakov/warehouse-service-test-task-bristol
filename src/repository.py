from motor.motor_asyncio import AsyncIOMotorCollection
from src import type_hints, interfaces, models


class MongoRepo(interfaces.IWarehouseMonitorRepo):
    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    async def get_movement_info_by_id(
        self,
        movement_id: str,
        needed_fields: type_hints.MOVEMENT_NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
    ) -> list[models.MovementObj]:
        query = {"data.movement_id": movement_id}

        if needed_fields:
            cursor = self._collection.find(query, projection=needed_fields)
        else:
            cursor = self._collection.find(query)

        if order_by:
            cursor = cursor.sort(order_by)

        results: type_hints.MONGO_MOVEMENT_LIST = await cursor.to_list(length=None)
        result = await self._deserialize_movement_data_objs(results)
        return result

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
