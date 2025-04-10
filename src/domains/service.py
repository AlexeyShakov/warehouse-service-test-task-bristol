from src.infrastructure.mongo import repository, type_hints
from src.serializers import from_kafka_pydantic
from src.domains import models, interfaces, exceptions
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime, timezone


class WarehouseMonitorService:
    """
    Т.к. логики не так много, то я объединил все в один сервис.
    Если разрастется логика работы с продуктами и передвижениями, возможно стоит разбить на разные сервисы
    """

    def __init__(self, repo: interfaces.IWarehouseMonitorRepo) -> None:
        self._repo = repo

    async def get_movement_info(
        self,
        movement_id: str,
        needed_fields: type_hints.NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
    ) -> models.MovementDiffInfo:
        # TODO в данном словаре мы опираемся на реализацию Mongo, что неправильно для слоя сервиса.
        # По-хорошему здесь должны быть универсальная структура, а вот на уровне репозитория, она бы подстраивалась под БД
        # Переделать, если хватит времени
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
        # TODO в данном словаре мы опираемся на реализацию Mongo, что неправильно для слоя сервиса.
        # По-хорошему здесь должны быть универсальная структура, а вот на уровне репозитория, она бы подстраивалась под БД
        # Переделать, если хватит времени
        filtering_data = {
            "data.warehouse_id": warehouse_id,
            "data.product_id": product_id,
        }
        remaining_product_info = await self._repo.get_remaining_product_info(
            filtering_data, needed_fields
        )
        if not remaining_product_info:
            raise exceptions.WarehouseOrProductNotFound(warehouse_id, product_id)
        remaining_quantity = await self._calculate_remaining_product_quantity(
            remaining_product_info
        )
        return remaining_quantity

    async def _calculate_remaining_product_quantity(
        self, remaining_product_info: list[models.RemainingProduct]
    ) -> int:
        remaining_quantity = 0
        for product in remaining_product_info:
            if product.event == "arrival":
                remaining_quantity += product.quantity
            else:
                remaining_quantity -= product.quantity
        return remaining_quantity

    async def add_product_movement_event(
        self, product_movement_message: from_kafka_pydantic.WarehouseEvent
    ) -> None:
        quantity = product_movement_message.data.quantity
        message_id = product_movement_message.id
        if product_movement_message.data.event == "departure":
            await self._process_product_quantity_when_departure(
                product_id=product_movement_message.data.product_id,
                warehouse_id=product_movement_message.data.warehouse_id,
                quantity=quantity,
                message_id=message_id,
            )
        needed_fields = {
            "source": 1,
            "data.movement_id": 1,
            "data.warehouse_id": 1,
            "data.timestamp": 1,
            "data.quantity": 1,
            "data.event": 1,
        }

        filtering_data = {"data.movement_id": product_movement_message.data.movement_id}
        added_movements = await self._repo.get_movement_info(
            filtering_data=filtering_data, needed_fields=needed_fields
        )
        await self._validate_current_movement_if_exists_else(
            existing_movements=added_movements,
            current_movement_timestamp=product_movement_message.data.timestamp,
            current_movement_event=product_movement_message.data.event,
            message_id=message_id,
        )
        await self._repo.add_product_movement_event(product_movement_message)

    async def _process_product_quantity_when_departure(
        self, product_id: str, warehouse_id: str, quantity: int, message_id: str
    ) -> None:
        filtering_data = {
            "data.warehouse_id": warehouse_id,
            "data.product_id": product_id,
        }
        needed_fields = {
            "source": 1,
            "data.movement_id": 1,
            "data.warehouse_id": 1,
            "data.timestamp": 1,
            "data.quantity": 1,
            "data.event": 1,
        }
        remaining_product_info = await self._repo.get_remaining_product_info(
            filtering_data, needed_fields
        )
        if not remaining_product_info:
            return
        remaining_quantity = await self._calculate_remaining_product_quantity(
            remaining_product_info
        )
        if remaining_quantity - quantity < 0:
            # Наверное, нужно посылать какое-то уведомление, если мы пытаемся взять больше товара чем нужно
            raise exceptions.ProductMovementValidationError(
                f"You are trying to send more product with id '{product_id}' from the warehouse with id '{warehouse_id}'\
                than there are.The current balance is {remaining_quantity}. Message id '{message_id}'"
            )

    async def _validate_current_movement_if_exists_else(
        self,
        existing_movements: list[models.MovementObj],
        current_movement_timestamp: datetime,
        current_movement_event: models.MOVEMENT_EVENTS,
        message_id: str,
    ) -> None:
        if not existing_movements:
            return
        if len(existing_movements) == 2:
            raise exceptions.ProductMovementValidationError(
                f"There are already two messages with the same movement. This message with id '{message_id}' is redundant."
            )
        if existing_movements[0].event == current_movement_event:
            raise exceptions.ProductMovementValidationError(
                f"Trying to add movement with event that already exists. The message id '{message_id}'"
            )
        existing_ts = existing_movements[0].timestamp
        if existing_ts.tzinfo is None:
            existing_ts = existing_ts.replace(tzinfo=timezone.utc)
        if (
            existing_movements[0].event == "departure"
            and current_movement_timestamp <= existing_ts
        ):
            raise exceptions.ProductMovementValidationError(
                f"Arrival time must be greater than departure time. The message id '{message_id}'"
            )


async def get_service(
    events_collection: AsyncIOMotorCollection,
) -> WarehouseMonitorService:
    repo = repository.MongoRepo(events_collection)
    return WarehouseMonitorService(repo)
