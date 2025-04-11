from pathlib import Path
import asyncio
import json
from aiokafka import AIOKafkaProducer

from src.config import get_project_settings
from src.infrastructure.kafka import connection, consume
from src.infrastructure.mongo.connection import get_db_connection, close_connection
from src.infrastructure import logger

SETTINGS = get_project_settings()

DATA_DIR = Path(__file__).parent / "data"
PRIMARY_FILE = DATA_DIR / "warehouse_events.json"
FALLBACK_FILE = DATA_DIR / "test_warehouse_events.json"

sem = asyncio.Semaphore(SETTINGS.max_concurrent_sends)


async def fill_db():
    background_task = set()
    consumer_task = None
    try:
        await get_db_connection()
        await connection.init_kafka_producer()
        consumer_task = asyncio.create_task(consume.consume_messages())
        background_task.add(consumer_task)
        await _fill_db(connection.PRODUCER)
    except Exception as e:
        logger.LOGGER.exception(f"Ошибка при заполнении БД: {e}")
    finally:
        await connection.stop_kafka()
        await close_connection()
        if consumer_task in background_task:
            background_task.discard(consumer_task)
            consumer_task.cancel()


async def _fill_db(producer: AIOKafkaProducer):
    events = await _get_data()

    async def send(event: dict):
        async with sem:
            await producer.send_and_wait(
                SETTINGS.kafka_topic, json.dumps(event).encode("utf-8")
            )

    await asyncio.gather(*(send(event) for event in events))
    logger.LOGGER.info("БД заполнена")


async def _get_data():
    file_path = PRIMARY_FILE if PRIMARY_FILE.exists() else FALLBACK_FILE
    file = await _open_file(file_path)
    return file


async def _open_file(file_path: Path) -> list[dict]:
    def _read_json():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return await asyncio.to_thread(_read_json)
