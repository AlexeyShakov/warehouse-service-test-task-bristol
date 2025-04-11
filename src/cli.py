import asyncio
import typer
from src.utils.fill_db import fill_db
from src.infrastructure import logger

app = typer.Typer()


@app.command()
def fill_database():
    """
    Для заполнения БД и проверки работоспособности kafka-консьюмера
    """
    logger.LOGGER.info("Launch filling db")
    asyncio.run(fill_db())
