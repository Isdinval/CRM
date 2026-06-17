from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/crm"
    API_V1_STR: str = "/api/v1"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
