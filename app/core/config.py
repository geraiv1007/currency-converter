from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import Field, PositiveInt
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


class JWTSettings(EnvFileSettings):

    SECRET_KEY: str = Field(description='Secret key for encoding/decoding JWT')
    ACCESS_TOKEN_EXPIRES: PositiveInt = Field(default=300, description='Lifetime of an access token in seconds')
    REFRESH_TOKEN_EXPIRES: PositiveInt = Field(default=604800, description='Lifetime of a refresh token in seconds')
    ALGORITHM: Literal['HS256', 'RS256', 'PS256', 'EdDSA', 'ES256'] = Field(
        default='HS256',
        description='One of digital signature algorithms for decoding/encoding JWT'
    )

    model_config = SettingsConfigDict(
        extra='forbid',
        env_file=Path(__file__).resolve().parent.parent.parent / '.env.jwt'
    )


class ExternalOAuthSettings(EnvFileSettings):

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    TOKEN_URI: str
    AUTH_URI: str
    #CERT_URI: str

class GoogleAuthSettings(EnvFileSettings):

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    TOKEN_URI: str
    AUTH_URI: str
    CERT_URI: str

    model_config = SettingsConfigDict(
        extra='forbid',
        env_file=Path(__file__).resolve().parent.parent.parent / '.env.google'
    )


class YandexAuthSettings(EnvFileSettings):

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    AUTH_URI: str
    TOKEN_URI: str
    USER_INFO_URI: str

    model_config = SettingsConfigDict(
        extra='forbid',
        env_file=Path(__file__).resolve().parent.parent.parent / '.env.yandex'
    )


class DBSettings(EnvFileSettings):

    DIALECT: str = Field(default='postgres')
    DRIVER: str = Field(default='asyncpg')
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int
    DATABASE: str

    model_config = SettingsConfigDict(
        extra='forbid',
        env_prefix='DB_',
        env_file=Path(__file__).resolve().parent.parent.parent / '.env.db'
    )

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
