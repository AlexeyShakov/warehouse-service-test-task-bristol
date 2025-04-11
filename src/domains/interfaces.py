from abc import ABC, abstractmethod
from src.infrastructure.mongo import type_hints
from src.domains import models
from src.serializers import from_kafka_pydantic
from typing import Any


class IWarehouseMonitorRepo(ABC):
    @abstractmethod
    async def get_movement_info(
        self,
        needed_fields: type_hints.NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
        filtering_data: type_hints.FILTERING_DATA = None,
    ) -> list[models.MovementObj]:
        raise NotImplementedError()

    @abstractmethod
    async def get_remaining_product_info(
        self,
        filtering_data: dict[str, Any],
        needed_fields: type_hints.NEEDED_FIELDS = None,
    ) -> list[models.RemainingProduct]:
        raise NotImplementedError()

    @abstractmethod
    async def add_product_movement_event(
        self, product_movement_message: from_kafka_pydantic.WarehouseEvent
    ) -> None:
        raise NotImplementedError()
