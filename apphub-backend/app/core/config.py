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

    # 개발 편의: true면 startup 시 create_all() 실행 (운영에서는 false)
    APP_INIT_DB: bool = False

    # ✅ 추가: DB 없으면 init.sql로 DB+테이블 생성
    APP_INIT_SQL: bool = False
    APP_INIT_SQL_PATH: str = "app/db/sql/init.sql"

    AUTH_KNOX_HEADER: str = "x-knox-id"
    BATCH_TIMEZONE: str = "Asia/Seoul"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        # mysql+aiomysql://user:pass@host:port/db
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_ASYNC_BOOTSTRAP(self) -> str:
        # ✅ DB가 없어도 붙기 위한 URL (db name 없이 서버에만 연결)
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/"
        )

settings = Settings()
