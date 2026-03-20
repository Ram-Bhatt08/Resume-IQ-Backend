import re
from typing import Dict, Any, List, Tuple
import spacy
from datetime import datetime
from collections import defaultdict

class ExperienceAnalyzer:
    """
    Analyzes work experience relevance and match
    """
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        
    async def analyze(self, resume: str, jd: str) -> Dict[str, Any]:
        """
        Analyze experience match between resume and job description
        """
        # Extract experience from resume
        resume_experience = await self._extract_experience(resume)
        
        # Extract requirements from JD
        jd_requirements = await self._extract_requirements(jd)
        
        # Calculate match scores
        years_match = self._calculate_years_match(
            resume_experience["total_years"],
            jd_requirements["min_years"],
            jd_requirements["max_years"]
        )
        
        role_match = await self._calculate_role_match(
            resume_experience["roles"],
            jd_requirements["required_roles"]
        )
        
        responsibility_match = await self._calculate_responsibility_match(
            resume_experience["responsibilities"],
            jd_requirements["responsibilities"]
        )
        
        # Calculate overall match score
        weights = {"years": 0.3, "role": 0.4, "responsibilities": 0.3}
        overall_score = (
            years_match * weights["years"] +
            role_match * weights["role"] +
            responsibility_match * weights["responsibilities"]
        )
        
        # Calculate similarity score
        similarity_score = await self._calculate_similarity_score(
            resume_experience["description"],
            jd_requirements["description"]
        )
        
        return {
            "match_score": round(overall_score, 2),
            "total_years": resume_experience["total_years"],
            "required_years": jd_requirements["min_years"],
            "role_match_percentage": round(role_match * 100, 2),
            "responsibility_match_percentage": round(responsibility_match * 100, 2),
            "similarity_score": round(similarity_score, 2),
            "details": {
                "resume_roles": resume_experience["roles"][:5],
                "jd_roles": jd_requirements["required_roles"][:5],
                "matched_responsibilities": responsibility_match,
                "gaps": self._identify_gaps(resume_experience, jd_requirements)
            }
        }
    
    async def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract experience details from resume"""
        doc = self.nlp(text)
        
        experience = {
            "total_years": 0,
            "roles": [],
            "responsibilities": [],
            "description": text,
            "companies": []
        }
        
        # Extract years of experience using regex patterns
        year_patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs).*?(?:experience)',
            r'experience.*?(\d+)[\+]?\s*(?:years?|yrs)',
            r'(\d{4})\s*[-–—]\s*(?:present|current|now|today|\d{4})'
        ]
        
        total_months = 0
        for pattern in year_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                try:
                    if '-' in match.group():
                        # Handle date ranges
                        dates = re.findall(r'\d{4}', match.group())
                        if len(dates) >= 2:
                            months = (int(dates[1]) - int(dates[0])) * 12
                            total_months += months
                    else:
                        # Handle explicit years
                        years = int(match.group(1))
                        total_months += years * 12
                except (ValueError, IndexError):
                    continue
        
        experience["total_years"] = round(total_months / 12, 1)
        
        # Extract roles/titles
        role_indicators = ['engineer', 'developer', 'architect', 'lead', 'manager', 
                          'consultant', 'specialist', 'analyst', 'designer']
        
        for token in doc:
            if token.text.lower() in role_indicators:
                # Find the full title
                start = max(0, token.i - 3)
                end = min(len(doc), token.i + 2)
                title = doc[start:end].text
                if title not in experience["roles"]:
                    experience["roles"].append(title)
        
        return experience
    
    async def _extract_requirements(self, jd: str) -> Dict[str, Any]:
        """Extract experience requirements from job description"""
        requirements = {
            "min_years": 0,
            "max_years": 99,
            "required_roles": [],
            "responsibilities": [],
            "description": jd
        }
        
        # Extract required years
        year_patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs).*?(?:experience required|required experience)',
            r'minimum.*?(\d+)[\+]?\s*(?:years?|yrs)',
            r'at least.*?(\d+)[\+]?\s*(?:years?|yrs)'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, jd.lower())
            if match:
                try:
                    requirements["min_years"] = int(match.group(1))
                    break
                except (ValueError, IndexError):
                    continue
        
        # Extract role requirements
        doc = self.nlp(jd)
        role_indicators = ['engineer', 'developer', 'architect', 'lead', 'manager']
        
        for sent in doc.sents:
            if any(word in sent.text.lower() for word in ['role', 'position', 'title', 'looking for']):
                for token in sent:
                    if token.text.lower() in role_indicators:
                        start = max(0, token.i - 2)
                        end = min(len(doc), token.i + 1)
                        role = doc[start:end].text
                        if role not in requirements["required_roles"]:
                            requirements["required_roles"].append(role)
        
        return requirements
    
    def _calculate_years_match(self, resume_years: float, required_min: int, required_max: int) -> float:
        """Calculate years of experience match score"""
        if resume_years >= required_min:
            if required_max and resume_years > required_max:
                # Overqualified but still matches
                return 0.9
            return 1.0
        else:
            # Less experience than required
            return resume_years / required_min if required_min > 0 else 0
    
    async def _calculate_role_match(self, resume_roles: List[str], jd_roles: List[str]) -> float:
        """Calculate role/title match score"""
        if not jd_roles:
            return 0.5  # Neutral score if no specific role mentioned
        
        matched = 0
        for jd_role in jd_roles:
            for resume_role in resume_roles:
                if self._role_similarity(resume_role, jd_role) > 0.7:
                    matched += 1
                    break
        
        return matched / len(jd_roles)
    
    def _role_similarity(self, role1: str, role2: str) -> float:
        """Calculate semantic similarity between role titles"""
        doc1 = self.nlp(role1.lower())
        doc2 = self.nlp(role2.lower())
        
        if doc1.has_vector and doc2.has_vector:
            return doc1.similarity(doc2)
        return 0.0
    
    async def _calculate_responsibility_match(self, resume_resp: List[str], jd_resp: List[str]) -> float:
        """Calculate responsibilities match score"""
        if not jd_resp:
            return 0.5
        
        # Simplified matching - in production, use more sophisticated NLP
        return 0.7  # Placeholder
    
    async def _calculate_similarity_score(self, resume_text: str, jd_text: str) -> float:
        """Calculate semantic similarity between experience descriptions"""
        doc1 = self.nlp(resume_text)
        doc2 = self.nlp(jd_text)
        
        if doc1.has_vector and doc2.has_vector:
            return doc1.similarity(doc2)
        return 0.0
    
    def _identify_gaps(self, resume_exp: Dict[str, Any], jd_req: Dict[str, Any]) -> List[str]:
        """Identify experience gaps"""
        gaps = []
        
        if resume_exp["total_years"] < jd_req["min_years"]:
            gaps.append(f"Experience short by {jd_req['min_years'] - resume_exp['total_years']} years")
        
        if not resume_exp["roles"]:
            gaps.append("No relevant role experience found")
        
        return gaps
    