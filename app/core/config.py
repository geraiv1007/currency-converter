from dotenv import find_dotenv
from functools import lru_cache
from pydantic import BaseModel, Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from sqlalchemy import URL
from typing import Literal, Type, Tuple


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


class JWTSettings(BaseModel):

    SECRET_KEY: str = Field(description='Secret key for encoding/decoding JWT')
    ACCESS_TOKEN_EXPIRES: PositiveInt = Field(default=300, description='Lifetime of an access token in seconds')
    REFRESH_TOKEN_EXPIRES: PositiveInt = Field(default=604800, description='Lifetime of a refresh token in seconds')
    ALGORITHM: Literal['HS256', 'RS256', 'PS256', 'EdDSA', 'ES256'] = Field(
        default='HS256',
        description='One of digital signature algorithms for decoding/encoding JWT'
    )


class CurrencyApiSettings(BaseModel):

    API_KEY: str
    API_URL: str


class ExternalAuthSettings(BaseModel):

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    TOKEN_URI: str
    AUTH_URI: str


class GoogleAuthSettings(ExternalAuthSettings):

    CERT_URI: str


class YandexAuthSettings(ExternalAuthSettings):

    USER_INFO_URI: str


class DBSettings(BaseModel):

    DIALECT: str = Field(default='postgres')
    DRIVER: str = Field(default='asyncpg')
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int
    DATABASE: str


    @property
    def connection_url(self):
        connect_args = {
            'drivername': f'{self.DIALECT}+{self.DRIVER}',
            'username': self.USERNAME,
            'password': self.PASSWORD,
            'host': self.HOST,
            'port': self.PORT,
            'database': self.DATABASE
        }
        url = URL.create(**connect_args)
        return str(url)


class CacheSettings(BaseModel):

    HOST: str
    PORT: int
    DB: str
    PASSWORD: str | None = Field(default=None)


class Settings(EnvFileSettings):

    DB: DBSettings
    CACHE: CacheSettings
    JWT: JWTSettings
    GOOGLE: GoogleAuthSettings
    YANDEX: YandexAuthSettings
    CURRENCY: CurrencyApiSettings

    model_config = SettingsConfigDict(
        extra='forbid',
        env_nested_delimiter='__',
        env_file=find_dotenv()
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()