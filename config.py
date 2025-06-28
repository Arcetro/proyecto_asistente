from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')

    GOOGLE_API_KEY: str
    ADMIN_PHONE_NUMBER: str
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str
    AIRTABLE_TABLE_NAME: str

# Creamos una única instancia que importaremos en otros archivos
settings = Settings()