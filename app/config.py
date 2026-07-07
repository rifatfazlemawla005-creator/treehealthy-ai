# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Parameter Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    # Parameter AI Engine
    GOOGLE_API_KEY: str

    DATASET_PATH: str = "E:\\HealtyCare\\ml_model\\data\diabetes_binary_5050split_health_indicators_BRFSS2015.csv"

    # Otomatis baca file .env di root folder
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Inisialisasi object settings agar bisa di-import di file lain
settings = Settings()
