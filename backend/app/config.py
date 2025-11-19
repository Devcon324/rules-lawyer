from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Rules Lawyer API"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # JWT Settings
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth Settings
    AUTH_USERNAME: str = ""
    AUTH_PASSWORD: str = ""
    
    # Database Settings (to be configured later)
    # DATABASE_URL: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

