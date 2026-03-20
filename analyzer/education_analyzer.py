import re
from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class Education:
    degree: str
    field: str
    institution: str
    year: int
    gpa: float

class EducationAnalyzer:
    """
    Analyzes educational background and match with proper field detection
    """
    
    def __init__(self):
        # Degree weights with proper hierarchy
        self.degree_weights = {
            "phd": 1.0,
            "doctorate": 1.0,
            "master": 0.9,
            "mba": 0.9,
            "bachelor": 0.8,
            "bba": 0.8,  # Bachelor of Business Administration
            "bca": 0.8,  # Bachelor of Computer Applications
            "associate": 0.6,
            "diploma": 0.5,
            "certificate": 0.4,
            "higher secondary": 0.3,
            "secondary": 0.2,
            "unknown": 0.1
        }
        
        # Degree field categories with comprehensive keywords
        self.degree_fields = {
            "computer_science": {
                "keywords": [
                    "computer science", "cs", "cse", "information technology", "it",
                    "software engineering", "computer engineering", "information systems",
                    "computing", "data science", "computer application", "bca", "mca",
                    "information science", "informatics", "software development"
                ],
                "weight": 1.0,
                "related": ["engineering", "data_science", "mathematics"]
            },
            "marketing": {
                "keywords": [
                    "marketing", "business administration", "bba", "mba",
                    "business management", "commerce", "b.com", "m.com",
                    "advertising", "public relations", "pr", "mass communication",
                    "digital marketing", "brand management", "market research"
                ],
                "weight": 1.0,
                "related": ["business", "communications"]
            },
            "business": {
                "keywords": [
                    "business", "management", "administration", "finance",
                    "accounting", "economics", "commerce", "entrepreneurship",
                    "business studies", "business administration", "bba", "mba",
                    "human resources", "hr", "operations", "supply chain"
                ],
                "weight": 1.0,
                "related": ["marketing", "finance"]
            },
            "engineering": {
                "keywords": [
                    "engineering", "b.tech", "m.tech", "be", "me",
                    "electrical", "mechanical", "civil", "electronics",
                    "chemical", "biotechnology", "biomedical", "aerospace",
                    "computer engineering", "software engineering"
                ],
                "weight": 1.0,
                "related": ["computer_science", "technology"]
            },
            "data_science": {
                "keywords": [
                    "data science", "analytics", "data analytics", "business analytics",
                    "machine learning", "artificial intelligence", "ai", "ml",
                    "statistics", "biostatistics", "data engineering", "big data"
                ],
                "weight": 1.0,
                "related": ["computer_science", "mathematics", "statistics"]
            },
            "design": {
                "keywords": [
                    "design", "graphic design", "ui/ux", "visual design",
                    "fashion design", "interior design", "communication design",
                    "industrial design", "product design", "web design"
                ],
                "weight": 1.0,
                "related": ["arts", "creative"]
            },
            "communications": {
                "keywords": [
                    "communications", "mass communication", "journalism",
                    "media studies", "public relations", "pr", "advertising",
                    "broadcasting", "digital media", "corporate communication"
                ],
                "weight": 1.0,
                "related": ["marketing", "english"]
            },
            "mathematics": {
                "keywords": [
                    "mathematics", "applied mathematics", "pure mathematics",
                    "statistics", "actuarial science", "mathematical science"
                ],
                "weight": 1.0,
                "related": ["data_science", "computer_science", "physics"]
            },
            "physics": {
                "keywords": [
                    "physics", "applied physics", "theoretical physics",
                    "engineering physics", "physical science"
                ],
                "weight": 1.0,
                "related": ["engineering", "mathematics"]
            },
            "chemistry": {
                "keywords": [
                    "chemistry", "applied chemistry", "chemical science",
                    "biochemistry", "organic chemistry", "inorganic chemistry"
                ],
                "weight": 1.0,
                "related": ["chemical engineering", "biology"]
            },
            "biology": {
                "keywords": [
                    "biology", "biological science", "biotechnology",
                    "microbiology", "molecular biology", "genetics",
                    "biochemistry", "bioinformatics"
                ],
                "weight": 1.0,
                "related": ["biotechnology", "medicine"]
            }
        }
        
        # Field synonyms for better matching
        self.field_synonyms = {
            "computer science": ["cs", "cse", "computing", "software engineering", "it", "information technology"],
            "engineering": ["engineer", "engineering", "b.tech", "be"],
            "business": ["business administration", "management", "mba", "bba", "commerce", "b.com"],
            "marketing": ["marketing", "digital marketing", "brand management", "advertising"],
            "data science": ["data", "analytics", "machine learning", "ai", "ml", "data analysis"],
            "mathematics": ["math", "mathematics", "applied math", "statistics"],
            "communications": ["communication", "mass comm", "journalism", "pr", "public relations"],
            "design": ["design", "graphic design", "ui/ux", "visual design"]
        }
    
    async def analyze(self, resume: str, jd: str) -> Dict[str, Any]:
        """
        Analyze education match between resume and job description
        
        Args:
            resume: Resume text
            jd: Job description text
            
        Returns:
            Dictionary with education analysis results
        """
        # Extract education from resume
        resume_education = await self._extract_education(resume)
        
        # Extract education requirements from JD
        jd_requirements = await self._extract_requirements(jd)
        
        # Calculate degree level match
        degree_match = self._calculate_degree_match(
            resume_education["highest_degree"],
            jd_requirements["required_degree"]
        )
        
        # Calculate field match (most important for specific roles)
        field_match = self._calculate_field_match(
            resume_education["field_category"],
            jd_requirements["required_fields"],
            jd_requirements["preferred_fields"]
        )
        
        # Determine if field is required or preferred
        is_field_required = len(jd_requirements["required_fields"]) > 0
        
        # Calculate overall match score with appropriate weights
        if is_field_required:
            # Field is required - heavily weight it
            overall_score = field_match * 0.7 + degree_match * 0.3
        else:
            # Field is preferred but not required
            overall_score = field_match * 0.4 + degree_match * 0.6
        
        # Check if minimum requirements are met
        meets_minimum = self._meets_minimum_requirements(
            resume_education, 
            jd_requirements,
            is_field_required
        )
        
        # Generate detailed explanation
        explanation = self._generate_explanation(
            resume_education,
            jd_requirements,
            degree_match,
            field_match,
            meets_minimum
        )
        
        return {
            "match_score": round(overall_score, 2),
            "degree_match_percentage": round(degree_match * 100, 2),
            "field_match_percentage": round(field_match * 100, 2),
            "highest_degree": resume_education["highest_degree"],
            "degree_display": resume_education["degree_display"],
            "field_of_study": resume_education["field_display"],
            "field_category": resume_education["field_category"],
            "required_degree": jd_requirements["required_degree"],
            "required_fields": jd_requirements["required_fields_display"],
            "preferred_fields": jd_requirements["preferred_fields_display"],
            "meets_minimum": meets_minimum,
            "explanation": explanation,
            "details": {
                "education_history": resume_education["history"][:3],
                "requirements": {
                    "degree": jd_requirements["required_degree"],
                    "required_fields": jd_requirements["required_fields"],
                    "preferred_fields": jd_requirements["preferred_fields"]
                }
            }
        }
    
    async def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education details from resume"""
        education = {
            "highest_degree": "unknown",
            "degree_display": "Unknown",
            "field_category": "unknown",
            "field_display": "Unknown",
            "fields": [],
            "history": [],
            "institutions": []
        }
        
        # Find education section
        edu_section = self._find_education_section(text)
        if not edu_section:
            edu_section = text[:1000]  # Use first 1000 chars if no section found
        
        # Extract degree information
        degree_info = self._extract_degree_info(edu_section)
        if degree_info["degree"]:
            education["highest_degree"] = degree_info["degree"]
            education["degree_display"] = degree_info["display"]
        
        # Extract field of study
        field_info = self._extract_field_info(edu_section)
        if field_info["category"]:
            education["field_category"] = field_info["category"]
            education["field_display"] = field_info["display"]
            education["fields"].append(field_info["category"])
        
        # Extract institutions
        institutions = self._extract_institutions(edu_section)
        education["institutions"] = institutions
        
        # Extract education history lines
        lines = edu_section.split('\n')
        for line in lines[:10]:  # First 10 lines of education section
            if line.strip() and len(line.strip()) > 10:
                education["history"].append(line.strip())
        
        return education
    
    async def _extract_requirements(self, jd: str) -> Dict[str, Any]:
        """Extract education requirements from job description"""
        requirements = {
            "required_degree": "unknown",
            "required_fields": [],
            "required_fields_display": [],
            "preferred_fields": [],
            "preferred_fields_display": [],
            "min_gpa": None,
            "certifications": []
        }
        
        jd_lower = jd.lower()
        
        # Find education-related sections
        required_section = self._find_required_section(jd)
        preferred_section = self._find_preferred_section(jd)
        
        # Extract degree requirements
        degree_info = self._extract_degree_requirement(jd_lower, required_section)
        if degree_info["degree"]:
            requirements["required_degree"] = degree_info["degree"]
        
        # Extract field requirements from required section
        if required_section:
            fields = self._extract_fields_from_text(required_section)
            for field in fields:
                if field not in requirements["required_fields"]:
                    requirements["required_fields"].append(field["category"])
                    requirements["required_fields_display"].append(field["display"])
        
        # Extract field requirements from preferred section
        if preferred_section:
            fields = self._extract_fields_from_text(preferred_section)
            for field in fields:
                if field["category"] not in requirements["required_fields"]:
                    requirements["preferred_fields"].append(field["category"])
                    requirements["preferred_fields_display"].append(field["display"])
        
        # If no fields found in sections, check whole JD
        if not requirements["required_fields"] and not requirements["preferred_fields"]:
            fields = self._extract_fields_from_text(jd)
            # Assume first found fields are required
            for i, field in enumerate(fields[:2]):
                if i == 0:
                    requirements["required_fields"].append(field["category"])
                    requirements["required_fields_display"].append(field["display"])
                else:
                    requirements["preferred_fields"].append(field["category"])
                    requirements["preferred_fields_display"].append(field["display"])
        
        return requirements
    
    def _find_education_section(self, text: str) -> str:
        """Find the education section in resume"""
        patterns = [
            r'(?:education|academic background|qualifications|educational qualifications)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*(?:experience|work|projects|skills|achievements|certifications|$))',
            r'(?:education|academic background|qualifications)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _find_required_section(self, jd: str) -> str:
        """Find required qualifications section in JD"""
        patterns = [
            r'(?:required qualifications?|qualifications? required|minimum qualifications?|requirements?)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*(?:preferred|nice to have|responsibilities|about|$))',
            r'(?:required|minimum)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*(?:preferred|nice to have|$))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _find_preferred_section(self, jd: str) -> str:
        """Find preferred qualifications section in JD"""
        patterns = [
            r'(?:preferred qualifications?|nice to have|plus|additional qualifications?)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*(?:responsibilities|about|benefits|$))',
            r'(?:preferred|nice to have)[\s\n]*:?[\s\n]*(.*?)(?=\n\s*(?:responsibilities|$))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_degree_info(self, text: str) -> Dict[str, str]:
        """Extract degree information from text"""
        result = {
            "degree": "unknown",
            "display": "Unknown"
        }
        
        text_lower = text.lower()
        
        # Check for degree keywords in order of hierarchy
        degree_keywords = [
            ("phd", ["phd", "doctorate", "doctoral", "d.phil", "doctor of"]),
            ("master", ["master", "mba", "msc", "m.s.", "m.tech", "m.e.", "m.com", "mca", "pg"]),
            ("bachelor", ["bachelor", "bs", "ba", "b.s.", "b.a.", "b.tech", "b.e.", "b.com", "bba", "bca"]),
            ("associate", ["associate", "diploma", "a.s.", "a.a."]),
            ("higher secondary", ["higher secondary", "12th", "hsc", "a levels", "intermediate"]),
            ("secondary", ["secondary", "10th", "ssc", "o levels", "matriculation"])
        ]
        
        for degree, keywords in degree_keywords:
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the actual degree name
                    lines = text.split('\n')
                    for line in lines:
                        if keyword in line.lower():
                            result["display"] = line.strip()[:100]
                            break
                    result["degree"] = degree
                    return result
        
        return result
    
    def _extract_field_info(self, text: str) -> Dict[str, str]:
        """Extract field of study information"""
        result = {
            "category": "unknown",
            "display": "Unknown"
        }
        
        text_lower = text.lower()
        
        # Check each field category
        for category, field_info in self.degree_fields.items():
            for keyword in field_info["keywords"]:
                if keyword in text_lower:
                    # Find the actual field name
                    lines = text.split('\n')
                    for line in lines:
                        if keyword in line.lower():
                            # Clean up the line
                            field_text = line.strip()
                            # Remove degree prefixes
                            field_text = re.sub(r'^(bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?b\.?a\.?|b\.?t ech|m\.?tech)\s+(?:of|in)?\s*', '', field_text, flags=re.IGNORECASE)
                            if field_text and len(field_text) < 100:
                                result["display"] = field_text
                                break
                    
                    result["category"] = category
                    if result["display"] == "Unknown":
                        result["display"] = category.replace('_', ' ').title()
                    
                    return result
        
        return result
    
    def _extract_fields_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract field categories from text"""
        fields = []
        text_lower = text.lower()
        
        for category, field_info in self.degree_fields.items():
            for keyword in field_info["keywords"]:
                if keyword in text_lower:
                    # Check if this is likely referring to education
                    context_pattern = rf'(?:degree|field|major|study|background).{{0,30}}{re.escape(keyword)}'
                    if re.search(context_pattern, text_lower):
                        fields.append({
                            "category": category,
                            "display": category.replace('_', ' ').title()
                        })
                        break
        
        return fields
    
    def _extract_degree_requirement(self, jd_lower: str, required_section: str) -> Dict[str, str]:
        """Extract degree requirement from JD"""
        result = {
            "degree": "unknown",
            "display": "Unknown"
        }
        
        # Check required section first
        if required_section:
            section_lower = required_section.lower()
            degree_keywords = [
                ("phd", ["phd", "doctorate"]),
                ("master", ["master", "mba", "msc"]),
                ("bachelor", ["bachelor", "bs", "ba", "b.tech", "b.e.", "bba", "bca"]),
                ("associate", ["associate", "diploma"])
            ]
            
            for degree, keywords in degree_keywords:
                for keyword in keywords:
                    if keyword in section_lower:
                        result["degree"] = degree
                        result["display"] = keyword.upper()
                        return result
        
        # Check whole JD
        for degree, keywords in degree_keywords:
            for keyword in keywords:
                if keyword in jd_lower:
                    # Check if it's mentioned as requirement
                    if re.search(rf'(?:required|minimum|must have|need).{{0,30}}{re.escape(keyword)}', jd_lower):
                        result["degree"] = degree
                        result["display"] = keyword.upper()
                        return result
        
        # Default to bachelor for most tech jobs
        if any(word in jd_lower for word in ["developer", "engineer", "programmer", "software"]):
            result["degree"] = "bachelor"
            result["display"] = "Bachelor's Degree"
        
        return result
    
    def _extract_institutions(self, text: str) -> List[str]:
        """Extract institution names from text"""
        institutions = []
        
        # Common institution indicators
        patterns = [
            r'(?:university|college|institute|school)\s+of\s+[\w\s]+',
            r'[\w\s]+(?:university|college|institute|school)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                inst = match.group().strip()
                if inst and len(inst) > 5 and inst not in institutions:
                    institutions.append(inst)
        
        return institutions[:3]  # Return top 3
    
    def _calculate_degree_match(self, resume_degree: str, required_degree: str) -> float:
        """Calculate degree level match score"""
        resume_score = self.degree_weights.get(resume_degree, 0.1)
        required_score = self.degree_weights.get(required_degree, 0.5)
        
        if required_score == 0:
            return 1.0
        
        if resume_score >= required_score:
            return 1.0
        else:
            return resume_score / required_score
    
    def _calculate_field_match(self, resume_field: str, required_fields: List[str], preferred_fields: List[str]) -> float:
        """Calculate field of study match score"""
        # If no fields specified, assume any field is acceptable
        if not required_fields and not preferred_fields:
            return 0.8
        
        # Check required fields first
        for req_field in required_fields:
            if resume_field == req_field:
                return 1.0
            # Check related fields
            if req_field in self.degree_fields and resume_field in self.degree_fields[req_field].get("related", []):
                return 0.9
        
        # Check preferred fields
        for pref_field in preferred_fields:
            if resume_field == pref_field:
                return 0.8
            if pref_field in self.degree_fields and resume_field in self.degree_fields[pref_field].get("related", []):
                return 0.7
        
        # No match found
        if required_fields:
            return 0.0  # Required field not matched
        else:
            return 0.3  # Low match for preferred fields
    
    def _meets_minimum_requirements(self, resume_edu: Dict, jd_req: Dict, field_required: bool) -> bool:
        """Check if education meets minimum requirements"""
        # Check degree level
        resume_level = self.degree_weights.get(resume_edu["highest_degree"], 0)
        required_level = self.degree_weights.get(jd_req["required_degree"], 0)
        
        if resume_level < required_level:
            return False
        
        # Check field if required
        if field_required and jd_req["required_fields"]:
            field_match = self._calculate_field_match(
                resume_edu["field_category"],
                jd_req["required_fields"],
                []
            )
            if field_match < 0.5:
                return False
        
        return True
    
    def _generate_explanation(self, resume_edu: Dict, jd_req: Dict, degree_match: float, field_match: float, meets_minimum: bool) -> str:
        """Generate human-readable education explanation"""
        parts = []
        
        # Degree information
        if resume_edu["degree_display"] != "Unknown":
            parts.append(f"📋 {resume_edu['degree_display']}")
        
        # Field information
        if resume_edu["field_display"] != "Unknown":
            parts.append(f"📚 Field: {resume_edu['field_display']}")
        
        # Requirement information
        if jd_req["required_fields_display"]:
            required = ', '.join(jd_req["required_fields_display"][:2])
            parts.append(f"🔍 Required: {required}")
        
        # Match status
        if degree_match >= 0.8 and field_match >= 0.7:
            parts.append("✅ Education matches well")
        elif meets_minimum:
            parts.append("⚠️ Meets minimum requirements")
        else:
            parts.append("❌ Does not meet requirements")
        
        # Specific field mismatch
        if jd_req["required_fields"] and field_match < 0.5:
            required = jd_req["required_fields_display"][0] if jd_req["required_fields_display"] else "specific field"
            parts.append(f"❌ Field mismatch: Looking for {required}")
        
        return " | ".join(parts)
    