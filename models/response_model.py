# response_model.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ScoreBreakdown(BaseModel):
    skills: float
    experience: float
    education: float
    projects: float

class DetailedAnalysis(BaseModel):
    skills: Dict[str, Any]
    experience: Dict[str, Any]
    education: Dict[str, Any]
    projects: Dict[str, Any]
    score_breakdown: ScoreBreakdown

class AnalysisResponse(BaseModel):
    session_id: str
    decision: str  # "Shortlisted" or "Rejected"
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    similarity_score: float
    explanation: str
    detailed_analysis: DetailedAnalysis
    reasoning_steps: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "decision": "Shortlisted",
                "score": 85.5,
                "matched_skills": ["python", "react", "aws"],
                "missing_skills": ["kubernetes"],
                "similarity_score": 78.3,
                "explanation": "Strong match with 3/4 required skills...",
                "detailed_analysis": {},
                "reasoning_steps": []
            }
        }
        