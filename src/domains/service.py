from src.infrastructure.mongo import repository, type_hints
from src.domains import models, interfaces, exceptions
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime


class WarehouseMonitorService:
    """
    Т.к. логики не так много, то я объединил все в один сервис.
    Если разрастется логика работы с продуктами и передвижениями, возможно стоит разбить на разные сервисы
    """

    def __init__(self, repo: interfaces.IWarehouseMonitorRepo) -> None:
        self._repo = repo

    async def get_movement_info(
        self,
        movement_id,
        needed_fields: type_hints.NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
    ) -> models.MovementDiffInfo:
        movements = await self._repo.get_movement_info(
            needed_fields, order_by, filtering_data={"data.movement_id": movement_id}
        )
        if not movements:
            raise exceptions.MovementNotFound(movement_id)
        if len(movements) == 2:
            movement_info = await self._get_movement_info_if_source_and_destination(
                movements[0], movements[1]
            )
        else:
            movement_info = await self._get_movement_info_if_source_or_destination(
                movements[0]
            )
        return movement_info

    async def _get_movement_info_if_source_and_destination(
        self, earlier_movement: models.MovementObj, later_movement: models.MovementObj
    ) -> models.MovementDiffInfo:
        quantity_diff = abs(later_movement.quantity - earlier_movement.quantity)
        timestamp_diff = await self._get_timestamp_diff(
            later_movement.timestamp, earlier_movement.timestamp
        )
        return models.MovementDiffInfo(
            movement_id=earlier_movement.movement_id,
            quantity_diff=quantity_diff,
            source=earlier_movement.warehouse_id,
            destination=later_movement.warehouse_id,
            timestamp_diff=models.TimestampDiff(**timestamp_diff),
        )

    async def _get_timestamp_diff(
        self, later_timestamp: datetime, earlier_timestamp: datetime
    ) -> dict[str, int]:
        timestamp_delta = abs(later_timestamp - earlier_timestamp)
        days = timestamp_delta.days
        seconds = timestamp_delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return {"days": days, "hours": hours, "minutes": minutes}

    async def _get_movement_info_if_source_or_destination(
        self, movement: models.MovementObj
    ) -> models.MovementDiffInfo:
        # question - не совсем понятно, чем заполнять timestamp_diff и quantity, поэтому заполню на свое усмотрение
        return models.MovementDiffInfo(
            movement_id=movement.movement_id,
            quantity_diff=movement.quantity,
            source=movement.warehouse_id,
            destination=None,
            timestamp_diff=None,
        )

    async def get_remaining_product_quantity(
        self,
        warehouse_id: str,
        product_id: str,
        needed_fields: type_hints.NEEDED_FIELDS = None,
    ) -> int:
        # TODO надо проверить, что такие warehouse_id и product_id существуют
        filtering_data = {
            "data.warehouse_id": warehouse_id,
            "data.product_id": product_id,
        }
        remaining_product_info = await self._repo.get_remaining_product_info(
            filtering_data, needed_fields
        )
        remaining_quantity = 0
        for product in remaining_product_info:
            if product.event == "arrival":
                remaining_quantity += product.quantity
            else:
                remaining_quantity -= product.quantity
        return remaining_quantity


async def get_service(
    events_collection: AsyncIOMotorCollection,
) -> WarehouseMonitorService:
    repo = repository.MongoRepo(events_collection)
    return WarehouseMonitorService(repo)
