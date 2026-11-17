from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DPM ENTERPRISE ERP"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://dpm_erp:change-this-local-password@localhost:5432/dpm_erp"
    cors_origins: str = "http://localhost:3000"
    jwt_secret_key: str = "CHANGE-ME-BEFORE-DEPLOYMENT-USE-32-PLUS-RANDOM-BYTES"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
