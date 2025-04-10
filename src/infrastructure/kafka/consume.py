from src.serializers import from_kafka_pydantic
from pydantic import ValidationError
from src.infrastructure.mongo.connection import get_events_collection
from src.domains import (
    service as warehouse_monitor_service,
)
from src.infrastructure import logger


async def process_kafka_message(product_movement_message: dict) -> None:
    try:
        validated_product_movement_message = await _validate_message(
            product_movement_message
        )
    except ValidationError as e:
        logger.LOGGER.exception(
            f"Ошибка валидаци сообщения из кафки. Сообщение: {product_movement_message}, ошибка: {e}"
        )
        return
    events_collection = await get_events_collection()
    service = await warehouse_monitor_service.get_service(events_collection)
    try:
        await service.add_product_movement_event(validated_product_movement_message)
    except Exception as e:
        # Наверное, нужно отправлять какие-то уведомления о том, что из брокера пришли кривые сообщения
        logger.LOGGER.exception(f"Неизвестная ошибка при добавлении сообщения из кафки в систему. \
        Сообщение: {product_movement_message}, ошибка: {e}")


async def _validate_message(message: dict) -> from_kafka_pydantic.WarehouseEvent:
    return from_kafka_pydantic.WarehouseEvent(**message)
