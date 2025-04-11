from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from src.infrastructure.kafka.connection import init_kafka_producer
from src.routers import warehouse_routes, movements_routes
from src.infrastructure.mongo.connection import get_db_connection, close_connection
from src.infrastructure import logger
from src.infrastructure.kafka import connection, consume


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_db_connection()
        logger.LOGGER.info("Подключение к БД установлено")
        await init_kafka_producer()

        app.state.consumer_task = asyncio.create_task(consume.consume_messages())
        yield
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.LOGGER.exception(f"Неизвестная ошибка при подключении к БД {e}")
    finally:
        consumer_task = getattr(app.state, "consumer_task", None)
        if consumer_task:
            consumer_task.cancel()
        await connection.stop_kafka()
        await close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(warehouse_routes)
app.include_router(movements_routes)
