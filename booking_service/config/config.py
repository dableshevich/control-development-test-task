from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Booking Service"
    API_PREFIX: str = "/api"

    # DATABASE CONFIG
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "booking_service"

    # REDIS CONFIG
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_password"

    @property
    def REDIS_URL(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                username=None,
                password=self.REDIS_PASSWORD,
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=None,
            )
        )

    @property
    def POSTGRES_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=f"{self.POSTGRES_DB}",
            )
        )


settings = Settings()
