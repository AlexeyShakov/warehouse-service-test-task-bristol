from abc import ABC, abstractmethod
from src import models, type_hints


class IWarehouseMonitorRepo(ABC):
    @abstractmethod
    async def get_movement_info_by_id(
        self,
        movement_id: str,
        needed_fields: type_hints.MOVEMENT_NEEDED_FIELDS = None,
        order_by: type_hints.ORDER_BY = None,
    ) -> list[models.MovementObj]:
        raise NotImplementedError()
