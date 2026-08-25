from pydantic import BaseModel, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from order_service.settings_utils import normalize_base_url


class DatabaseSettings(BaseModel):
    name: str
    username: str
    password: SecretStr
    host: str
    port: int

    @property
    def url(self) -> str:
        return (
            f'postgresql+asyncpg://'
            f'{self.username}:{self.password.get_secret_value()}'
            f'@{self.host}:{self.port}/{self.name}'
        )


class CapashinoSettings(BaseModel):
    base_url: str
    api_key: SecretStr

    @property
    def api_secret_key(self) -> str:
        return self.api_key.get_secret_value()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    CAPASHINO_BASE_URL: str
    CAPASHINO_API_KEY: SecretStr

    ORDER_SERVICE_CALLBACK_BASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CONSUMER_GROUP_ID: str = 'order-service'

    OUTBOX_MAX_ATTEMPTS: int = 5
    OUTBOX_BATCH_LIMIT: int = 50
    OUTBOX_DISPATCH_INTERVAL_SECONDS: float = 5.0

    @field_validator('ORDER_SERVICE_CALLBACK_BASE_URL')
    @classmethod
    def _ensure_scheme(cls, value: str) -> str:
        return normalize_base_url(value)

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            name=self.POSTGRES_DATABASE_NAME,
            username=self.POSTGRES_USERNAME,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
        )

    @property
    def capashino(self) -> CapashinoSettings:
        return CapashinoSettings(
            base_url=self.CAPASHINO_BASE_URL,
            api_key=self.CAPASHINO_API_KEY,
        )


settings = Settings()
