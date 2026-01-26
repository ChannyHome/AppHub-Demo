from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "AppHub API"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8500

    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"

    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    APP_INIT_DB: bool = False

    AUTH_KNOX_HEADER: str = "x-knox-id"
    BATCH_TIMEZONE: str = "Asia/Seoul"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        # mysql+aiomysql://user:pass@host:port/db
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()
