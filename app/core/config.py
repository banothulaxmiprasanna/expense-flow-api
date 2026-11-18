from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    DATABASE_URL: str = Field(...)
    SECRET_KEY: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    MAX_EXPENSE_AMOUNT: float = 50000.0
    REQUIRE_RECEIPT_ABOVE: float = 50.0

    model_config = {
        "env_prefix": "EXPENSEFLOW_",
        "env_file": ".env",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
