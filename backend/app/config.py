from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DPM ENTERPRISE ERP"
    app_env: str = "development"
    database_url: str = "sqlite:///./dpm_erp.db"
    cors_origins: str = "http://localhost:3000"
    public_base_url: str = "https://www.dpmenterprise.in"
    jwt_secret_key: str = "CHANGE-ME-BEFORE-DEPLOYMENT-USE-32-PLUS-RANDOM-BYTES"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    bootstrap_admin_name: str = "DPM Enterprise Administrator"
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
