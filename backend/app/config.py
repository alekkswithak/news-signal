from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "news_analyzer"

    gnews_api_key: str = ""
    gnews_base_url: str = "https://gnews.io/api/v4"

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-nano"

    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
