# request_model.py
from pydantic import BaseModel, Field, validator
from typing import Optional

class ResumeJDRequest(BaseModel):
    """Request model for resume analysis"""
    
    resume: str = Field(
        ..., 
        min_length=50,
        max_length=50000,
        description="Candidate resume text"
    )
    jd: str = Field(
        ..., 
        min_length=50,
        max_length=20000,
        description="Job description text"
    )
    job_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional job title for context"
    )
    
    @validator('resume')
    def validate_resume(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Resume must be at least 50 characters')
        return v.strip()
    
    @validator('jd')
    def validate_jd(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Job description must be at least 50 characters')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume": "Experienced software engineer with 5 years in full-stack development...",
                "jd": "Looking for a Senior Full Stack Developer with expertise in React, Node.js...",
                "job_title": "Senior Full Stack Developer"
            }
        }
        