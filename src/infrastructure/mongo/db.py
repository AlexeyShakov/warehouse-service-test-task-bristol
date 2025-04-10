from typing import Optional, Dict, Tuple

import backoff
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure

from src.config import get_project_settings

SETTINGS = get_project_settings()


class MongoClient:
    """
    Синглтон для подключения к Mongo
    """

    __instance: Optional["MongoClient"] = None

    def __new__(cls, *args: Tuple, **kwargs: Dict) -> "MongoClient":
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, mongo_uri: str) -> None:
        self._mongo_uri = mongo_uri
        self._connection: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

    async def get_connection(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        if self._connection:
            return self._connection
        await self._set_connection(self._mongo_uri)
        return self._connection

    @backoff.on_exception(
        backoff.constant,
        ConnectionFailure,
        interval=0.5,
        max_tries=2,
        jitter=None,
        # TODO сюда надо добавить логгер
    )
    async def _set_connection(self, mongo_uri):
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        await self._check_connection(client)
        self._connection = client

    async def _check_connection(
        self, client: motor.motor_asyncio.AsyncIOMotorClient
    ) -> None:
        await client.admin.command("ping")

    def get_collection(
        self, db_name: str, collection_name: str
    ) -> motor.motor_asyncio.AsyncIOMotorCollection:
        if not self._connection:
            raise RuntimeError("MongoDB connection is not initialized")
        return self._connection[db_name][collection_name]

    async def close_connection(self):
        if not self._connection:
            return
        self._connection.close()
        self._connection = None


_MONGO_DB_CLIENT = MongoClient(
    f"mongodb://{SETTINGS.mongo_initdb_root_username}:{SETTINGS.mongo_initdb_root_password}@{SETTINGS.mongo_host}:{SETTINGS.db_port}/"
)


async def get_db_connection() -> motor.motor_asyncio.AsyncIOMotorClient:
    return await _MONGO_DB_CLIENT.get_connection()


async def close_connection() -> None:
    await _MONGO_DB_CLIENT.close_connection()


async def get_events_collection() -> motor.motor_asyncio.AsyncIOMotorCollection:
    return _MONGO_DB_CLIENT.get_collection(
        db_name=SETTINGS.mongo_db_name, collection_name="events"
    )
