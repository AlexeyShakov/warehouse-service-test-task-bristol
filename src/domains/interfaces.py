from abc import ABC, abstractmethod
from src.infrastructure.mongo import type_hints
from src.domains import models


class IWarehouseMonitorRepo(ABC):
    @abstractmethod
    async def get_movement_info(
        self,
        needed_fields: type_hints.NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
        filtering_data: type_hints.FILTERING_DATA = None,
    ) -> list[models.MovementObj]:
        raise NotImplementedError()

    async def get_remaining_product_info(
        self,
        filtering_data: dict[str, str],
        needed_fields: type_hints.NEEDED_FIELDS = None,
    ) -> list[models.RemainingProduct]:
        raise NotImplementedError()
