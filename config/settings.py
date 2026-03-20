from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "AI Resume Shortlisting Agent"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # AI Model Settings
    spacy_model: str = "en_core_web_lg"
    similarity_threshold: float = 0.7
    
    # Scoring weights
    skill_weight: float = 0.4
    experience_weight: float = 0.3
    education_weight: float = 0.15
    project_weight: float = 0.15
    
    # Decision threshold
    shortlist_threshold: float = 70.0
    
    # CORS settings
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()
