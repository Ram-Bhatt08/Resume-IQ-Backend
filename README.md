# 🚀 AI-Powered Resume Shortlisting Agent
An intelligent, AI-driven system that automatically analyzes and shortlists resumes based on job descriptions using advanced NLP and machine learning techniques.

# 🎯 Overview
The AI-Powered Resume Shortlisting Agent automates the initial screening of job applications by intelligently matching candidate resumes with job descriptions. It uses a multi-faceted analysis approach including skill extraction, experience evaluation, education assessment, and project relevance scoring to make accurate shortlisting decisions.

# ✨ Features
Core Capabilities
Intelligent Resume Parsing: Automatically extracts and structures information from resumes

Job Description Analysis: Identifies key requirements, preferred skills, and role expectations

Multi-dimensional Scoring: Evaluates candidates across skills, experience, education, and projects

Real-time Processing: Provides instant analysis results

Detailed Reasoning: Explains why a candidate was shortlisted or rejected

# Advanced Features
Category Detection: Automatically identifies job categories (software, marketing, data science, etc.)

Context-Aware Skill Extraction: Recognizes skills in context, not just keyword matching

Experience Quality Assessment: Evaluates the quality and relevance of work experience

Education Field Matching: Checks if degree fields match job requirements

Project Relevance Analysis: Assesses how well projects align with required technologies

Semantic Similarity: Uses NLP to understand meaning beyond keywords

# Technical Features
RESTful API: Easy integration with any frontend application

CORS Enabled: Ready for cross-origin requests

Async Processing: Handles multiple requests efficiently

Comprehensive Logging: Detailed logs for debugging and monitoring

Configurable Weights: Adjust scoring parameters based on requirements

Timeout Handling: Prevents hanging on complex analyses

# File Structure 
backend/
│   ├── main.py
│   ├── agent/
│   │   ├── resume_agent.py
│   │   ├── agent_prompts.py
│   │   └── agent_config.py
│   ├── analyzer/
│   │   ├── enhanced_skill_extractor.py
│   │   ├── experience_analyzer.py
│   │   ├── education_analyzer.py
│   │   └── project_analyzer.py
│   ├── models/
│   │   ├── request_model.py
│   │   └── response_model.py
│   ├── utils/
│   │   ├── constants.py
│   │   └── text_processor.py
│   ├── config/
│   │   └── settings.py
│   ├── requirements.txt
│   └── .env

# Component Breakdown
FastAPI Backend (main.py): Handles HTTP requests, CORS, and routing

Agent Core (agent/): Orchestrates the analysis process

Analyzers (analyzer/): Specialized modules for different aspects

Models (models/): Pydantic models for request/response validation

Utils (utils/): Helper functions and constants

Config (config/): Environment-based configuration

# 💻 Tech Stack
Backend
Python 3.10+: Core programming language

FastAPI: Modern web framework for APIs

Uvicorn: ASGI server for high performance

Pydantic: Data validation and settings management

# NLP & ML
spaCy: Industrial-strength NLP library

scikit-learn: Machine learning utilities

NLTK: Natural language toolkit

Sentence-Transformers: For semantic similarity (optional)

# Data Processing
Regex: Pattern matching for text extraction

Pandas: Data manipulation and analysis

NumPy: Numerical computing

# Development & Deployment
python-dotenv: Environment variable management

pytest: Testing framework

black: Code formatting

isort: Import sorting
