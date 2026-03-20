from pydantic import BaseModel
from typing import Optional

class AgentConfig(BaseModel):
    """Configuration for the Resume Shortlisting Agent"""
    
    # Model settings
    spacy_model: str = "en_core_web_lg"
    
    # Scoring weights
    skill_weight: float = 0.40
    experience_weight: float = 0.30
    education_weight: float = 0.15
    project_weight: float = 0.15
    
    # Decision threshold
    shortlist_threshold: float = 70.0
    
    # Analysis settings
    min_resume_length: int = 50
    min_jd_length: int = 50
    max_skills_to_return: int = 20
    
    # Similarity settings
    similarity_threshold: float = 0.7
    use_semantic_matching: bool = True
    
    class Config:
        arbitrary_types_allowed = True
        