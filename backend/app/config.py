from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DPM ENTERPRISE ERP"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://dpm_erp:change-this-local-password@localhost:5432/dpm_erp"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
