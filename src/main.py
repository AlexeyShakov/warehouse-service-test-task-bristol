from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from src.routers import warehouse_routes, movements_routes
from src.infrastructure.db import get_db_connection, close_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await get_db_connection()
        # TODO добавить логгер
        yield
    except asyncio.CancelledError:
        pass
    except Exception:
        # TODO добавить логгер
        pass
    finally:
        await close_connection()


app = FastAPI(lifespan=lifespan)

app.include_router(warehouse_routes)
app.include_router(movements_routes)
