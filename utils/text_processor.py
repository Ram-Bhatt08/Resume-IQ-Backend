# text_processor.py
import re
from typing import List
import spacy

nlp = spacy.load("en_core_web_sm")

def preprocess_text(text: str) -> str:
    """
    Preprocess text for analysis
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s\.\,\-\:\;\(\)\[\]]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove multiple line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_sections(text: str) -> dict:
    """
    Extract common resume sections
    """
    sections = {}
    
    # Common section headers
    section_patterns = {
        'summary': r'(summary|profile|objective)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)',
        'experience': r'(experience|work experience|employment)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)',
        'education': r'(education|academic background)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)',
        'skills': r'(skills|technical skills|competencies)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)',
        'projects': r'(projects|key projects)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)',
        'certifications': r'(certifications|certificates)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)'
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections[section_name] = match.group(2).strip()
    
    return sections

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words
    """
    doc = nlp(text)
    return [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
