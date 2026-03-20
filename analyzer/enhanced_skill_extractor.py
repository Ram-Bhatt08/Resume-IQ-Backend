import re
from typing import Set, List, Dict, Any, Optional
import asyncio
from collections import defaultdict
import spacy
from utils.constants import (
    TECHNICAL_SKILLS, SOFT_SKILLS, SKILL_SYNONYMS,
    SKILL_PROFICIENCY_INDICATORS
)

class EnhancedSkillExtractor:
    """
    Advanced skill extractor with context awareness and proficiency detection
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            # Fallback to smaller model if large model not available
            self.nlp = spacy.load("en_core_web_sm")
        self.technical_skills = TECHNICAL_SKILLS
        self.soft_skills = SOFT_SKILLS
        self.skill_synonyms = SKILL_SYNONYMS
        self.proficiency_indicators = SKILL_PROFICIENCY_INDICATORS
        
    async def extract_all_skills(self, text: str) -> Set[str]:
        """Extract all skills with context and proficiency"""
        doc = self.nlp(text.lower())
        
        # Technical skills extraction
        technical = await self._extract_technical_skills(doc)
        
        # Soft skills extraction  
        soft = await self._extract_soft_skills(doc)
        
        # Extract skills from phrases and context
        contextual = await self._extract_contextual_skills(doc)
        
        return technical.union(soft).union(contextual)
    
    async def extract_required_skills(self, jd_text: str) -> Set[str]:
        """Extract required skills from job description with importance"""
        doc = self.nlp(jd_text.lower())
        
        required_skills = set()
        preferred_skills = set()
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            # Check for requirement indicators
            if any(indicator in sent_text for indicator in ['required', 'must have', 'need', 'essential']):
                skills = await self._extract_technical_skills(sent)
                required_skills.update(skills)
            elif any(indicator in sent_text for indicator in ['preferred', 'nice to have', 'plus']):
                skills = await self._extract_technical_skills(sent)
                preferred_skills.update(skills)
        
        return required_skills.union(preferred_skills)
    
    async def _extract_technical_skills(self, doc) -> Set[str]:
        """Extract technical skills using pattern matching and NER"""
        skills = set()
        
        for token in doc:
            token_text = token.text.lower()
            # Direct skill matching
            for skill in self.technical_skills:
                if skill in token_text or self._skill_similarity(token_text, skill) > 0.8:
                    skills.add(skill)
                    break
            
            # Check for skill combinations (e.g., "machine learning")
            if token.i < len(doc) - 1:
                bigram = f"{token_text} {doc[token.i + 1].text.lower()}"
                for skill in self.technical_skills:
                    if skill in bigram or self._skill_similarity(bigram, skill) > 0.8:
                        skills.add(skill)
        
        return skills
    
    async def _extract_soft_skills(self, doc) -> Set[str]:
        """Extract soft skills from text"""
        skills = set()
        
        for token in doc:
            token_text = token.text.lower()
            for skill in self.soft_skills:
                if skill in token_text or self._skill_similarity(token_text, skill) > 0.7:
                    skills.add(skill)
        
        return skills
    
    async def _extract_contextual_skills(self, doc) -> Set[str]:
        """Extract skills from context using dependency parsing"""
        skills = set()
        
        for token in doc:
            # Check for skills in context of tools/languages
            if token.dep_ in ['dobj', 'pobj'] and token.head.lemma_ in ['use', 'know', 'experience', 'work']:
                token_text = token.text.lower()
                for skill in self.technical_skills:
                    if skill in token_text:
                        skills.add(skill)
        
        return skills
    
    def _skill_similarity(self, word1: str, word2: str) -> float:
        """Calculate semantic similarity between words"""
        try:
            token1 = self.nlp(word1)
            token2 = self.nlp(word2)
            
            if token1.has_vector and token2.has_vector:
                return token1.similarity(token2)
        except:
            pass
        return 0.0
    
    async def get_skill_proficiency(self, text: str, skill: str) -> Dict[str, Any]:
        """Determine proficiency level for a skill"""
        doc = self.nlp(text.lower())
        
        proficiency = {
            "level": "basic",
            "years": None,
            "evidence": None
        }
        
        skill_pattern = re.compile(rf'\b{skill}\b.*?(\d+)[\+]?\s*(?:years?|yrs)', re.IGNORECASE)
        
        # Extract years of experience
        match = skill_pattern.search(text)
        if match:
            try:
                proficiency["years"] = int(match.group(1))
                if proficiency["years"] >= 5:
                    proficiency["level"] = "expert"
                elif proficiency["years"] >= 3:
                    proficiency["level"] = "intermediate"
            except:
                pass
        
        # Check for proficiency indicators
        text_lower = text.lower()
        for indicator, level in self.proficiency_indicators.items():
            if indicator in text_lower:
                proficiency["level"] = level
                proficiency["evidence"] = indicator
                break
        
        return proficiency
    