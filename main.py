# main.py - Complete updated file

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import logging
import time
import asyncio
import traceback
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# Logging Config
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Request Model
# ─────────────────────────────────────────────────────────────
class ResumeJDRequest(BaseModel):
    resume: str = Field(..., min_length=10)
    jd: str = Field(..., min_length=10)
    job_title: Optional[str] = None

    @validator("resume", "jd")
    def validate_text(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Input must be at least 10 characters")
        return v

# ─────────────────────────────────────────────────────────────
# Response Models - EXACTLY matching frontend expectations
# Based on Result.jsx which uses:
# - decision, score, matched_skills, missing_skills, similarity_score
# - explanation, detailed_analysis.score_breakdown, detailed_analysis.reasoning_loop
# - session_id
# ─────────────────────────────────────────────────────────────
class ScoreBreakdown(BaseModel):
    skills: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    projects: float = 0.0

class DetailedAnalysis(BaseModel):
    score_breakdown: ScoreBreakdown
    reasoning_loop: List[str] = []

class AnalysisResponse(BaseModel):
    decision: str
    score: float
    matched_skills: List[str]
    missing_skills: List[str]
    similarity_score: float
    explanation: str
    detailed_analysis: DetailedAnalysis
    session_id: str

    class Config:
        schema_extra = {
            "example": {
                "decision": "Shortlisted",
                "score": 88.0,
                "matched_skills": ["Python", "Machine Learning", "SQL", "Java", "JavaScript"],
                "missing_skills": ["Docker", "Kubernetes"],
                "similarity_score": 0.75,
                "explanation": "Candidate demonstrates strong skill alignment with 13 matched skill(s). Fresher with internship experience...",
                "detailed_analysis": {
                    "score_breakdown": {
                        "skills": 100.0,
                        "experience": 80.0,
                        "education": 100.0,
                        "projects": 60.0
                    },
                    "reasoning_loop": [
                        "Detected JD category: 'software_development' (81.0% confidence). Resume category: 'software_development'. Categories match.",
                        "Extracted 13 required skills from JD. Candidate matched 13 skill(s). Missing: 0 skill(s).",
                        "Experience: Fresher with internship experience... Role-match score: 70.0%.",
                        "Education: Bachelor degree in Computer Science — meets the educational requirement.",
                        "Projects: found 11 project(s) with relevance score 33.0%.",
                        "Weighted score: skills=100.0%×0.4, experience=80.0%×0.3, education=100.0%×0.15, projects=60.0%×0.15. Overall: 88.0%. Threshold: 70.0%. Decision: Shortlisted."
                    ]
                },
                "session_id": "req_1234567890"
            }
        }

# ─────────────────────────────────────────────────────────────
# Import Agent
# ─────────────────────────────────────────────────────────────
try:
    from agent.resume_agent import ResumeShortlistingAgent
    logger.info("✅ Agent imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    raise

# ─────────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Resume Shortlisting API",
    description="API for analyzing resumes against job descriptions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Initialize Agent
# ─────────────────────────────────────────────────────────────
resume_agent = None
try:
    resume_agent = ResumeShortlistingAgent()
    logger.info("✅ Agent initialized")
except Exception as e:
    logger.error(f"❌ Agent init failed: {e}")

# ─────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 3))
    return response

# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "AI Resume Shortlisting API",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy" if resume_agent else "error",
        "agent_ready": resume_agent is not None,
        "timestamp": datetime.now().isoformat()
    }

# ─────────────────────────────────────────────────────────────
# MAIN ANALYZE API - Updated to match frontend exactly
# ─────────────────────────────────────────────────────────────
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: ResumeJDRequest):
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"

    logger.info(f"📨 Request: {request_id}")

    if not resume_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        result = await asyncio.wait_for(
            resume_agent.analyze(
                resume=request.resume,
                job_description=request.jd
            ),
            timeout=30  # Increased timeout for complex analysis
        )

        # ── Ensure result has all required fields ──
        result = result or {}
        
        # Extract data from agent result
        decision = result.get("decision", "Rejected")
        score = float(result.get("match_percentage", result.get("score", 0)))
        
        # Skills
        matched_skills = [str(s).strip() for s in result.get("matched_skills", [])]
        missing_skills = [str(s).strip() for s in result.get("missing_skills", [])]
        
        # Similarity score
        similarity_score = float(result.get("similarity_score", 0))
        
        # Explanation (use reasoning if explanation not available)
        explanation = str(result.get("explanation", result.get("reasoning", "Analysis completed")))
        
        # Get detailed analysis
        detailed = result.get("detailed_analysis", {})
        
        # Score breakdown
        score_breakdown_data = detailed.get("score_breakdown", {})
        
        # Ensure all score breakdown fields exist
        skills_score = float(score_breakdown_data.get("skills", 0))
        experience_score = float(score_breakdown_data.get("experience", 0))
        education_score = float(score_breakdown_data.get("education", 0))
        projects_score = float(score_breakdown_data.get("projects", 0))
        
        # If scores are 0 but we have other data, calculate them
        if skills_score == 0 and len(matched_skills) > 0:
            # Calculate based on matched skills percentage
            total_skills = len(matched_skills) + len(missing_skills)
            if total_skills > 0:
                skills_score = (len(matched_skills) / total_skills) * 100
        
        score_breakdown = ScoreBreakdown(
            skills=round(skills_score, 1),
            experience=round(experience_score, 1),
            education=round(education_score, 1),
            projects=round(projects_score, 1)
        )
        
        # Reasoning loop
        reasoning_loop = detailed.get("reasoning_loop", [])
        if not reasoning_loop and "reasoning" in result:
            # Split reasoning into steps if available
            reasoning_loop = [result["reasoning"]]
        
        detailed_analysis = DetailedAnalysis(
            score_breakdown=score_breakdown,
            reasoning_loop=reasoning_loop
        )

        # Build final response - EXACTLY as frontend expects
        response = AnalysisResponse(
            decision=decision,
            score=round(score, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            similarity_score=round(similarity_score, 2),
            explanation=explanation,
            detailed_analysis=detailed_analysis,
            session_id=request_id
        )

        logger.info(f"✅ Done: {decision} ({score}%)")
        return response

    except asyncio.TimeoutError:
        logger.error(f"❌ Timeout for request {request_id}")
        raise HTTPException(status_code=408, detail="Analysis timeout - please try again")
    
    except Exception as e:
        logger.error(f"❌ Error for request {request_id}: {traceback.format_exc()}")
        
        # Return a graceful error response
        error_response = AnalysisResponse(
            decision="Error",
            score=0,
            matched_skills=[],
            missing_skills=[],
            similarity_score=0,
            explanation=f"An error occurred during analysis: {str(e)}",
            detailed_analysis=DetailedAnalysis(
                score_breakdown=ScoreBreakdown(),
                reasoning_loop=["Error occurred during analysis"]
            ),
            session_id=request_id
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )

# ─────────────────────────────────────────────────────────────
# Global Error Handler
# ─────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

# ─────────────────────────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Server starting...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
    