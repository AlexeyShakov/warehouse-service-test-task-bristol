from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    db_port: int
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str
    mongo_host: str
    mongo_db_name: str

    kafka_host: str
    kafka_topic: str


SETTINGS = GeneralApplicationSettings()


def get_project_settings() -> GeneralApplicationSettings:
    return SETTINGS
