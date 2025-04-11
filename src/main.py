from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio

from src.infrastructure.kafka.connection import init_kafka_producer
from src.routers import warehouse_routes, movements_routes
from src.infrastructure.mongo.connection import get_db_connection, close_connection
from src.infrastructure.redis import connection as redis_connection
from src.infrastructure import logger
from src.infrastructure.kafka import connection, consume

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


async def _init_cache():
    FastAPICache.init(
        RedisBackend(redis_connection.REDIS_CLIENT), prefix="fastapi-cache"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_db_connection()
        logger.LOGGER.info("Подключение к БД установлено")
        await init_kafka_producer()
        await _init_cache()

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


@app.get("/health", tags=["Health"])
async def health_check():
    return JSONResponse(content={"status": "ok"})
