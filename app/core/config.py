import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='UTF-8', extra="ignore",
    )

    POSTGRES_DSN: str

    REDIS_URL: str

    RABBITMQ_URL: str

    TELEGRAM_BOT_TOKEN: str

    JIRA_BASE_URL: str
    JIRA_USER_EMAIL: str
    JIRA_API_TOKEN: str
    JIRA_PROJECT_KEY: str

    GITHUB_WEBHOOK_SECRET: str
    ADMIN_TOKEN: str

    RULES_PATH: str

    LOG_LEVEL: str


def setup_logging(log_level: str) -> None:
    level_name = log_level
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
