from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from src.routers import warehouse_routes, movements_routes
from src.infrastructure.mongo.connection import get_db_connection, close_connection
from src.infrastructure import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_db_connection()
        logger.LOGGER.info("Подключение к БД установлено")
        yield
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.LOGGER.exception(f"Неизвестная ошибка при подключении к БД {e}")
    finally:
        await close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(warehouse_routes)
app.include_router(movements_routes)
