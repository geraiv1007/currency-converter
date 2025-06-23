from dotenv import find_dotenv
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from typing import Tuple, Type



class EnvFileSettings(BaseSettings):

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return dotenv_settings,


class KafkaSettings(BaseModel):

    HOST: str
    PORT: int


class MailSettings(BaseModel):

    HOSTNAME: str
    PORT: int
    USERNAME: str
    PASSWORD: str


class Settings(EnvFileSettings):

    KAFKA: KafkaSettings
    MAIL: MailSettings

    model_config = SettingsConfigDict(
        extra='forbid',
        env_nested_delimiter='__',
        env_file=find_dotenv('mail.env')
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()