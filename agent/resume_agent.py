# agent/resume_agent.py
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class AgentConfig:
    def __init__(self):
        self.skill_weight = 0.4
        self.experience_weight = 0.3
        self.education_weight = 0.15
        self.project_weight = 0.15
        self.shortlist_threshold = 70.0


class JobCategoryDetector:
    """Detects the job category from JD and resume"""

    def __init__(self):
        self.categories = {
            "software_development": {
                "keywords": [
                    "developer", "software", "programming", "code", "coding",
                    "java", "python", "javascript", "c++", "react", "node",
                    "backend", "frontend", "fullstack", "api", "database",
                    "algorithm", "data structure", "sql", "git", "github"
                ],
                "weight": 1.0
            },
            "marketing": {
                "keywords": [
                    "marketing", "digital marketing", "social media", "seo", "sem",
                    "content", "brand", "campaign", "analytics", "google analytics",
                    "facebook", "instagram", "linkedin", "advertising", "ppc",
                    "market research", "branding", "copywriting", "canva"
                ],
                "weight": 1.0
            },
            "data_science": {
                "keywords": [
                    "data science", "machine learning", "ai", "artificial intelligence",
                    "python", "r", "tensorflow", "pytorch", "pandas", "numpy",
                    "data analysis", "statistics", "visualization", "tableau",
                    "power bi", "sql", "big data", "hadoop", "spark"
                ],
                "weight": 1.0
            },
            "design": {
                "keywords": [
                    "designer", "ui", "ux", "graphic design", "photoshop",
                    "illustrator", "figma", "sketch", "adobe", "creative",
                    "wireframe", "prototype", "user interface", "user experience",
                    "visual design", "canva"
                ],
                "weight": 1.0
            },
            "sales": {
                "keywords": [
                    "sales", "business development", "account executive",
                    "client", "customer", "revenue", "lead generation",
                    "negotiation", "closing", "b2b", "b2c", "salesforce",
                    "crm", "pipeline", "quota"
                ],
                "weight": 1.0
            }
        }

    def detect_category(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}

        for category, data in self.categories.items():
            score = sum(data["weight"] for kw in data["keywords"] if kw in text_lower)
            scores[category] = score

        if not scores or max(scores.values()) == 0:
            return "unknown", 0

        best_category = max(scores, key=scores.get)
        max_possible = len(self.categories[best_category]["keywords"])
        normalized_score = min(scores[best_category] / max_possible * 100, 100)

        return best_category, normalized_score


class SkillExtractor:
    """Enhanced skill extractor with category-specific skills"""

    def __init__(self):
        logger.info("Initializing SkillExtractor...")
        self.skills_db = {
            "common": {
                "communication": ["communication", "verbal", "written"],
                "teamwork": ["teamwork", "collaboration", "team player"],
                "problem_solving": ["problem solving", "analytical", "critical thinking"],
                "time_management": ["time management", "organized", "deadline"],
                "leadership": ["leadership", "team lead", "mentoring"],
            },
            "software_development": {
                "python": ["python", "py", "python3"],
                "java": ["java", "j2ee", "javase"],
                "javascript": ["javascript", "js", "ecmascript"],
                "typescript": ["typescript", "ts"],
                "c": ["c language", "c programming"],
                "cpp": ["c++", "cpp", "cplusplus"],
                "c#": ["c#", "csharp"],
                "php": ["php"],
                "ruby": ["ruby"],
                "go": ["go", "golang"],
                "swift": ["swift"],
                "kotlin": ["kotlin"],
                "html": ["html", "html5"],
                "css": ["css", "css3"],
                "react": ["react", "reactjs", "react.js"],
                "angular": ["angular", "angularjs"],
                "vue": ["vue", "vuejs"],
                "node.js": ["node", "nodejs", "node.js"],
                "express.js": ["express", "express.js"],
                "django": ["django"],
                "flask": ["flask"],
                "spring": ["spring", "spring boot"],
                "spring boot": ["spring boot"],
                "sql": ["sql"],
                "mysql": ["mysql"],
                "postgresql": ["postgresql", "postgres"],
                "mongodb": ["mongodb", "mongo"],
                "oracle": ["oracle"],
                "data structures": ["data structures", "dsa"],
                "algorithms": ["algorithms", "algorithm"],
                "oop": ["oop", "object oriented"],
                "system design": ["system design"],
                "git": ["git", "github", "gitlab"],
                "docker": ["docker"],
                "kubernetes": ["kubernetes", "k8s"],
                "aws": ["aws", "amazon web services"],
                "azure": ["azure"],
                "rest api": ["rest", "rest api", "restful"],
                "api": ["api", "apis"],
            },
            "marketing": {
                "digital marketing": ["digital marketing", "online marketing"],
                "social media": ["social media", "facebook", "instagram", "linkedin", "twitter"],
                "seo": ["seo", "search engine optimization"],
                "sem": ["sem", "search engine marketing"],
                "content marketing": ["content", "copywriting", "blog"],
                "google analytics": ["google analytics", "analytics"],
                "google ads": ["google ads", "adwords"],
                "meta ads": ["meta ads", "facebook ads"],
                "email marketing": ["email marketing", "newsletter"],
                "market research": ["market research", "consumer behavior"],
                "branding": ["branding", "brand management"],
                "campaign": ["campaign", "campaign management"],
                "canva": ["canva"],
                "photoshop": ["photoshop", "adobe photoshop"],
                "excel": ["excel", "ms excel"],
                "powerpoint": ["powerpoint", "ppt"],
            },
            "data_science": {
                "python": ["python"],
                "r": ["r language", "r programming"],
                "tensorflow": ["tensorflow", "tf"],
                "pytorch": ["pytorch"],
                "pandas": ["pandas"],
                "numpy": ["numpy"],
                "scikit-learn": ["scikit-learn", "sklearn"],
                "tableau": ["tableau"],
                "power bi": ["power bi", "powerbi"],
                "sql": ["sql"],
                "machine learning": ["machine learning", "ml"],
                "deep learning": ["deep learning", "dl"],
                "data visualization": ["data visualization", "visualization"],
                "statistics": ["statistics", "statistical"],
            },
            "design": {
                "ui design": ["ui design", "user interface"],
                "ux design": ["ux design", "user experience"],
                "figma": ["figma"],
                "sketch": ["sketch"],
                "adobe xd": ["adobe xd", "xd"],
                "photoshop": ["photoshop"],
                "illustrator": ["illustrator"],
                "indesign": ["indesign"],
                "canva": ["canva"],
                "wireframing": ["wireframe", "wireframing"],
                "prototyping": ["prototype", "prototyping"],
                "graphic design": ["graphic design", "graphics"],
            },
            "sales": {
                "sales": ["sales", "selling"],
                "business development": ["business development", "biz dev"],
                "crm": ["crm", "salesforce", "hubspot"],
                "lead generation": ["lead generation", "prospecting"],
                "negotiation": ["negotiation", "closing"],
                "account management": ["account management", "client management"],
                "b2b": ["b2b", "business to business"],
                "b2c": ["b2c", "business to consumer"],
                "cold calling": ["cold calling", "cold calls"],
                "pipeline": ["pipeline", "sales pipeline"],
                "quota": ["quota", "sales target"],
            }
        }

        self.all_skills = {}
        for category, skills in self.skills_db.items():
            for skill, variations in skills.items():
                for variation in variations:
                    self.all_skills[variation] = {"skill": skill, "category": category}

        logger.info(f"SkillExtractor initialized with {len(self.all_skills)} variations")

    async def extract_all_skills(self, text: str) -> Dict[str, Set[str]]:
        skills_by_category = {cat: set() for cat in self.skills_db}
        text_lower = text.lower()

        for variation, data in self.all_skills.items():
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, text_lower):
                skills_by_category[data["category"]].add(data["skill"])

        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['skills:', 'technologies:', 'tools:', 'expertise:']):
                for part in re.split(r'[,•|]', line):
                    part = part.strip().lower()
                    for variation, data in self.all_skills.items():
                        if variation in part:
                            skills_by_category[data["category"]].add(data["skill"])

        return skills_by_category

    async def extract_required_skills(self, text: str, category: str = None) -> Dict[str, Set[str]]:
        all_skills = await self.extract_all_skills(text)
        if category and category in all_skills:
            return {"common": all_skills["common"], category: all_skills[category]}
        return all_skills


class ExperienceAnalyzer:
    async def analyze(self, resume: str, jd: str, category: str = None) -> Dict[str, Any]:
        resume_years = self._extract_years(resume)
        required_years = self._extract_years(jd)
        has_internship = self._has_internship(resume)
        internship_details = self._extract_internship_details(resume)

        if has_internship and resume_years == 0:
            resume_years = 0.5

        if category == "software_development":
            match_score = min(resume_years / required_years, 1.0) if required_years > 0 else (0.8 if has_internship else 0.6)
        else:
            match_score = min(resume_years / required_years * 1.2, 1.0) if required_years > 0 else (0.9 if has_internship else 0.7)

        resume_roles = self._extract_roles(resume)
        jd_roles = self._extract_roles(jd)

        role_match = 0.7
        for role in resume_roles:
            if any(jd_role in role for jd_role in jd_roles):
                role_match = 0.9
                break

        similarity_score = (match_score + role_match) / 2

        # Build experience summary
        if has_internship and resume_years <= 0.5:
            exp_summary = f"Fresher with internship experience"
            if internship_details:
                exp_summary += f" ({internship_details[:50]}...)"
        elif resume_years > 0:
            exp_summary = f"{resume_years} year(s) of relevant experience"
        else:
            exp_summary = "No prior experience detected"

        if required_years > 0 and resume_years < required_years:
            exp_summary += f" (role requires {required_years}+ years)"
        elif required_years > 0:
            exp_summary += f" — meets the {required_years}-year requirement"

        return {
            "match_score": round(match_score, 2),
            "similarity_score": round(similarity_score, 2),
            "total_years": resume_years,
            "required_years": required_years,
            "has_internship": has_internship,
            "internship_details": internship_details,
            "role_match_percentage": round(role_match * 100, 2),
            "experience_match": exp_summary,
            "details": {
                "resume_roles": resume_roles[:3],
                "jd_roles": jd_roles[:3]
            }
        }

    def _extract_years(self, text: str) -> float:
        patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs).*?(?:experience)',
            r'experience.*?(\d+)[\+]?\s*(?:years?|yrs)',
            r'(\d+)[\+]?\s*yea?r?s?',
            r'(\d+)[\+]?\s*\+\s*(?:years?|yrs)'
        ]
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return float(match.group(1))
                except Exception:
                    pass
        return 0

    def _has_internship(self, text: str) -> bool:
        return any(re.search(p, text.lower()) for p in [r'intern', r'internship', r'trainee'])

    def _extract_internship_details(self, text: str) -> str:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'intern' in line.lower() or 'internship' in line.lower():
                result = [line.strip()]
                if i + 1 < len(lines):
                    result.append(lines[i + 1].strip())
                return ' '.join(result)
        return ""

    def _extract_roles(self, text: str) -> List[str]:
        roles = []
        role_indicators = [
            'developer', 'engineer', 'marketing', 'designer', 'analyst',
            'manager', 'consultant', 'specialist', 'intern', 'trainee',
            'executive', 'associate', 'coordinator'
        ]
        text_lower = text.lower()
        for indicator in role_indicators:
            if indicator in text_lower:
                for match in re.finditer(rf'([\w\s-]{{0,20}}{indicator}[\w\s-]{{0,10}})', text_lower):
                    role = match.group(1).strip()
                    if role and role not in roles:
                        roles.append(role)
        return roles


class EducationAnalyzer:
    async def analyze(self, resume: str, jd: str) -> Dict[str, Any]:
        resume_degree = self._extract_highest_degree(resume)
        required_degree = self._extract_highest_degree(jd)
        resume_field = self._extract_field(resume)

        degree_values = {
            'phd': 1.0, 'master': 0.9, 'bachelor': 0.8,
            'associate': 0.6, 'diploma': 0.5,
            'higher secondary': 0.3, 'secondary': 0.2, 'unknown': 0.1
        }

        resume_value = degree_values.get(resume_degree, 0.1)
        required_value = degree_values.get(required_degree, 0.5)
        match_score = min(resume_value / required_value, 1.0) if required_value > 0 else 0.8

        # Build human-readable education_match string
        if resume_degree == 'unknown':
            edu_summary = "No formal degree detected in resume"
        else:
            edu_summary = f"{resume_degree.title()} degree"
            if resume_field != 'unknown':
                edu_summary += f" in {resume_field.title()}"
            if required_degree != 'unknown' and resume_value >= required_value:
                edu_summary += " — meets the educational requirement"
            elif required_degree != 'unknown':
                edu_summary += f" (role prefers {required_degree.title()})"

        return {
            "match_score": round(match_score, 2),
            "highest_degree": resume_degree,
            "required_degree": required_degree,
            "field_of_study": resume_field,
            "field_match_percentage": 100.0,
            "education_match": edu_summary,
            "details": {}
        }

    def _extract_highest_degree(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ['phd', 'doctorate', 'doctoral']):
            return 'phd'
        elif any(w in text_lower for w in ['master', 'mba', 'msc', 'm.s.', 'm.tech']):
            return 'master'
        elif any(w in text_lower for w in ['bachelor', 'bs', 'ba', 'b.s.', 'b.tech', 'b.e.', 'bba']):
            return 'bachelor'
        elif any(w in text_lower for w in ['associate', 'diploma']):
            return 'associate'
        elif any(w in text_lower for w in ['higher secondary', '12th']):
            return 'higher secondary'
        elif any(w in text_lower for w in ['secondary', '10th']):
            return 'secondary'
        return 'unknown'

    def _extract_field(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ['computer science', 'cs', 'cse', 'information technology', 'it']):
            return 'computer science'
        elif any(w in text_lower for w in ['marketing', 'business administration', 'bba', 'business']):
            return 'marketing'
        elif any(w in text_lower for w in ['data science', 'analytics']):
            return 'data science'
        elif any(w in text_lower for w in ['design', 'graphic design']):
            return 'design'
        return 'unknown'


class ProjectAnalyzer:
    """
    Enhanced project analyzer that properly detects projects from resume
    """
    
    async def analyze(self, resume: str, jd: str, category: str = None) -> Dict[str, Any]:
        projects = self._extract_projects(resume)
        project_count = len(projects)
        relevance_score = self._calculate_relevance(projects, jd, category)

        # Improved match score calculation
        if project_count == 0:
            match_score = 0.2  # Base score even with no projects
        else:
            # Base score from count (max 0.4 for 3+ projects)
            count_score = min(0.4, project_count * 0.15)
            # Relevance contributes up to 0.6
            match_score = min(count_score + (relevance_score * 0.6), 1.0)

        # Get project details for display
        project_details = []
        for project in projects[:3]:  # Show top 3 projects
            # Extract project name and technologies
            lines = project.split('\n')
            if lines:
                name = lines[0].strip()
                # Clean up project name
                name = re.sub(r'^[•\-●◆▶\d\.\s]+', '', name)
                if not name or len(name) < 3:
                    name = "Project"
                
                # Extract technologies used
                techs = []
                tech_keywords = ['java', 'python', 'react', 'node', 'mongodb', 'mysql', 
                               'express', 'javascript', 'html', 'css', 'mern', 'full stack',
                               'jdbc', 'swing', 'api', 'rest', 'jwt']
                
                for tech in tech_keywords:
                    if tech in project.lower():
                        techs.append(tech.title())
                
                # Get a brief description
                desc_lines = lines[1:4] if len(lines) > 1 else []
                description = ' '.join(desc_lines)[:150] + "..." if desc_lines else "No description available"
                
                project_details.append({
                    "name": name[:50],
                    "description": description,
                    "technologies": list(set(techs))[:5],  # Remove duplicates
                    "full_text": project[:200] + "..." if len(project) > 200 else project
                })

        return {
            "match_score": round(match_score, 2),
            "projects_count": project_count,
            "relevance_score": round(relevance_score, 2),
            "details": {
                "projects": project_details,
                "all_projects": [p[:150] + "..." if len(p) > 150 else p for p in projects[:5]]
            }
        }

    def _extract_projects(self, text: str) -> List[str]:
        """
        Improved project extraction that detects various project section formats
        Specifically designed to detect projects from the provided resume format
        """
        projects = []
        lines = text.split('\n')
        
        # Common project section headers
        project_headers = [
            'projects', 'PROJECTS', 'Project', 'PROJECT',
            'key projects', 'personal projects', 'my projects',
            'PROJECT EXPERIENCE', 'PROJECT WORK',
            'PROJECTS & ACHIEVEMENTS', 'PROJECTS AND ACHIEVEMENTS',
            '🔹 PROJECTS', '• PROJECTS', '## Projects'
        ]
        
        # Project name patterns (for resumes)
        project_name_patterns = [
            r'^([A-Z][a-zA-Z\s\-]+(?:System|Platform|App|Application|Tool|Website|Management|Scheduling|Quiz|Bank))',
            r'^([A-Z][a-zA-Z\s]+?(?:System|Application|Platform|Tool)[\s:])',
            r'^[•\-●◆▶]\s*([A-Z][a-zA-Z\s\-]+(?:System|Platform|App))',
            r'^\d+\.\s*([A-Z][a-zA-Z\s\-]+(?:System|Platform|App))',
            r'^([A-Z][a-zA-Z\s]+?(?:Management|Scheduling|Quiz|Bank))\s*(?:System|Platform|App)?'
        ]
        
        in_projects_section = False
        current_project = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check if we're entering projects section
            if not in_projects_section:
                for header in project_headers:
                    if header.lower() in line_lower:
                        # Check if this line is actually a header
                        if len(line_stripped) < 50 or ':' in line_stripped:
                            in_projects_section = True
                            current_project = []
                            break
                continue
            
            # Check if we're leaving projects section
            if in_projects_section and line_stripped:
                next_section_headers = ['experience', 'education', 'skills', 'achievements', 
                                       'certifications', 'training', 'technical', 'languages',
                                       'about', 'contact', 'summary', 'objective']
                
                # If we hit another major section header, exit projects section
                if any(header in line_lower and len(line_stripped) < 40 for header in next_section_headers):
                    if current_project:
                        projects.append('\n'.join(current_project))
                        current_project = []
                    in_projects_section = False
                    continue
            
            if in_projects_section:
                # Skip empty lines but use them as project separators
                if not line_stripped:
                    if current_project:
                        # Check if current project has substantial content
                        if len('\n'.join(current_project)) > 30:
                            projects.append('\n'.join(current_project))
                        current_project = []
                    continue
                
                # Check if this line starts a new project
                is_new_project = False
                for pattern in project_name_patterns:
                    match = re.match(pattern, line_stripped)
                    if match:
                        if current_project:
                            if len('\n'.join(current_project)) > 30:
                                projects.append('\n'.join(current_project))
                        current_project = [line_stripped]
                        is_new_project = True
                        break
                
                if not is_new_project:
                    # Check for bullet points that might start projects
                    if line_stripped.startswith(('•', '●', '◆', '▶', '-', '→')):
                        if current_project:
                            if len('\n'.join(current_project)) > 30:
                                projects.append('\n'.join(current_project))
                        current_project = [line_stripped]
                    else:
                        # Add to current project if it's not a section header
                        if current_project and not any(header in line_lower for header in next_section_headers):
                            current_project.append(line_stripped)
        
        # Add the last project if exists
        if current_project:
            if len('\n'.join(current_project)) > 30:
                projects.append('\n'.join(current_project))
        
        # If no projects found with the above logic, try alternative extraction
        if not projects:
            # Look for common project patterns anywhere in the resume
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                # Look for lines that might be project titles (specific to the resume format)
                project_keywords = ['System', 'App', 'Application', 'Platform', 'Tool', 
                                   'Management', 'Scheduling', 'Quiz', 'Bank', 'Website']
                
                if any(keyword in line_stripped for keyword in project_keywords):
                    # Check if this looks like a project title (not too long, not a header)
                    if len(line_stripped) < 100 and not any(header in line_stripped.lower() for header in 
                                                           ['experience', 'education', 'skills', 'achievements']):
                        project_desc = [line_stripped]
                        # Collect next few lines as description
                        for j in range(1, 5):
                            if i + j < len(lines):
                                next_line = lines[i + j].strip()
                                if next_line and len(next_line) > 10:
                                    # Stop if we hit another potential project or section
                                    if any(kw in next_line for kw in project_keywords) and len(next_line) < 60:
                                        break
                                    if any(header in next_line.lower() for header in 
                                          ['experience', 'education', 'skills']):
                                        break
                                    project_desc.append(next_line)
                        projects.append('\n'.join(project_desc))
        
        # Filter out very short or irrelevant entries
        filtered_projects = []
        for project in projects:
            # Check if project has meaningful content
            if len(project) > 30 and not project.lower().startswith(('experience', 'education', 'skills')):
                # Check for technology keywords to ensure it's a tech project
                tech_keywords = ['java', 'python', 'react', 'node', 'mongodb', 'mysql', 
                               'api', 'database', 'app', 'system', 'platform']
                if any(kw in project.lower() for kw in tech_keywords) or len(project) > 100:
                    filtered_projects.append(project)
        
        return filtered_projects

    def _calculate_relevance(self, projects: List[str], jd: str, category: str = None) -> float:
        if not projects:
            return 0.3  # Base relevance even with no projects
        
        jd_lower = jd.lower()
        project_text = ' '.join(projects).lower()
        
        # Category-specific keywords for relevance
        keyword_map = {
            "software_development": [
                'developed', 'built', 'created', 'designed', 'implemented',
                'application', 'system', 'platform', 'api', 'database',
                'frontend', 'backend', 'full-stack', 'full stack',
                'react', 'node', 'java', 'python', 'javascript',
                'mongodb', 'mysql', 'sql', 'rest', 'web', 'app',
                'mern', 'fullstack', 'jwt', 'authentication'
            ],
            "marketing": [
                'campaign', 'social media', 'content', 'brand', 'market',
                'engagement', 'audience', 'seo', 'analytics', 'growth'
            ],
            "data_science": [
                'data', 'analysis', 'model', 'prediction', 'visualization',
                'machine learning', 'ai', 'statistics', 'python', 'pandas'
            ],
            "design": [
                'design', 'ui', 'ux', 'prototype', 'wireframe', 'creative',
                'figma', 'photoshop', 'user interface', 'user experience'
            ],
        }
        
        # Get keywords for the category, or use generic if category not found
        keywords = keyword_map.get(category, [
            'project', 'developed', 'created', 'built', 'designed',
            'implemented', 'system', 'application', 'platform', 'tool'
        ])
        
        # Calculate relevance based on keyword matches
        keyword_matches = 0
        for kw in keywords:
            if kw in project_text:
                keyword_matches += 1
        
        # Calculate JD relevance (how well projects match JD content)
        jd_relevance = 0
        jd_words = set(jd_lower.split())
        for project in projects[:3]:  # Check top projects
            project_words = set(project.lower().split())
            common_words = project_words & jd_words
            # Count meaningful matches (words longer than 3 chars)
            meaningful_matches = sum(1 for word in common_words if len(word) > 3)
            jd_relevance = max(jd_relevance, min(meaningful_matches / 10, 0.5))
        
        # Calculate technology relevance
        tech_stack = ['java', 'python', 'javascript', 'react', 'node', 'mongodb', 
                     'mysql', 'express', 'api', 'rest', 'full stack', 'mern',
                     'jdbc', 'swing', 'jwt', 'authentication']
        tech_matches = sum(1 for tech in tech_stack if tech in project_text)
        tech_relevance = min(tech_matches / 8, 0.5)  # Adjusted denominator
        
        # Combine scores
        keyword_score = keyword_matches / (len(keywords) * 0.6) if keywords else 0.5
        keyword_score = min(keyword_score, 0.5)  # Cap at 0.5
        
        relevance = (keyword_score + jd_relevance + tech_relevance) / 3
        
        return min(relevance, 1.0)


class ResumeShortlistingAgent:
    def __init__(self, config: Optional[AgentConfig] = None):
        logger.info("Initializing ResumeShortlistingAgent...")
        self.config = config or AgentConfig()
        self.category_detector = JobCategoryDetector()
        self.skill_extractor = SkillExtractor()
        self.experience_analyzer = ExperienceAnalyzer()
        self.education_analyzer = EducationAnalyzer()
        self.project_analyzer = ProjectAnalyzer()
        self.reasoning_logs = {}
        logger.info("Agent initialized successfully")

    async def analyze(self, resume: str, job_description: str) -> Dict[str, Any]:
        session_id = str(uuid4())
        reasoning_steps = []
        start_time = time.time()

        logger.info(f"Starting analysis for session {session_id}")

        try:
            # ── Step 0: Category detection ──────────────────────────────
            jd_category, jd_category_score = self.category_detector.detect_category(job_description)
            resume_category, resume_category_score = self.category_detector.detect_category(resume)
            category_match = jd_category == resume_category or jd_category == "unknown"

            reasoning_steps.append(f"Detected JD category: '{jd_category}' ({jd_category_score:.1f}% confidence). Resume category: '{resume_category}'. Categories {'match' if category_match else 'do NOT match'}.")

            # ── Step 1: Skill extraction ─────────────────────────────────
            resume_skills_by_cat = await self.skill_extractor.extract_all_skills(resume)
            jd_skills_by_cat = await self.skill_extractor.extract_required_skills(job_description, jd_category)

            if jd_category in resume_skills_by_cat:
                relevant_resume_skills = resume_skills_by_cat.get(jd_category, set())
                relevant_jd_skills = jd_skills_by_cat.get(jd_category, set())
                common_skills = resume_skills_by_cat.get("common", set())
            else:
                relevant_resume_skills = set()
                relevant_jd_skills = set()
                for skills in resume_skills_by_cat.values():
                    relevant_resume_skills.update(skills)
                for skills in jd_skills_by_cat.values():
                    relevant_jd_skills.update(skills)
                common_skills = resume_skills_by_cat.get("common", set())

            matched_skills_set = set(relevant_resume_skills) & set(relevant_jd_skills)
            missing_skills_set = set(relevant_jd_skills) - set(relevant_resume_skills)
            common_matched = common_skills & set(relevant_jd_skills)
            matched_skills_set.update(common_matched)

            # Normalise skill names to Title Case for display
            matched_skills = sorted(s.title() for s in matched_skills_set)
            missing_skills = sorted(s.title() for s in missing_skills_set)

            reasoning_steps.append(f"Extracted {len(relevant_jd_skills)} required skills from JD. Candidate matched {len(matched_skills_set)} skill(s). Missing: {len(missing_skills_set)} skill(s).")

            # ── Step 2: Experience analysis ──────────────────────────────
            experience_analysis = await self.experience_analyzer.analyze(resume, job_description, jd_category)
            reasoning_steps.append(f"Experience: {experience_analysis['experience_match']}. Role-match score: {experience_analysis['role_match_percentage']}%.")

            # ── Step 3: Education analysis ───────────────────────────────
            education_analysis = await self.education_analyzer.analyze(resume, job_description)
            reasoning_steps.append(f"Education: {education_analysis['education_match']}.")

            # ── Step 4: Project analysis ─────────────────────────────────
            project_analysis = await self.project_analyzer.analyze(resume, job_description, jd_category)
            
            # Log project details for debugging
            projects_found = project_analysis.get('projects_count', 0)
            relevance = project_analysis.get('relevance_score', 0) * 100
            project_details = project_analysis.get('details', {}).get('projects', [])
            
            project_names = [p.get('name', 'Unknown') for p in project_details[:3]]
            project_techs = []
            for p in project_details[:3]:
                techs = p.get('technologies', [])
                if techs:
                    project_techs.append(f"{p.get('name', 'Project')}: {', '.join(techs[:3])}")

            reasoning_steps.append(
                f"Projects: found {projects_found} project(s) with relevance score {relevance:.1f}%. "
                f"Projects detected: {', '.join(project_names) if project_names else 'None'}. "
                f"{'Technologies: ' + '; '.join(project_techs) if project_techs else ''}"
            )

            # Ensure project analysis has all required fields
            if 'projects_count' not in project_analysis:
                project_analysis['projects_count'] = 0
            if 'relevance_score' not in project_analysis:
                project_analysis['relevance_score'] = 0.3
            if 'match_score' not in project_analysis:
                project_analysis['match_score'] = 0.3

            # ── Step 5: Score computation ────────────────────────────────
            if not category_match:
                overall_score = 20.0
                decision = "Rejected"
                reasoning_steps.append(f"Category mismatch (JD: {jd_category}, resume: {resume_category}). Final score forced to {overall_score}%.")
                reasoning = f"Category mismatch: the role requires a {jd_category.replace('_', ' ')} background but the resume reflects a {resume_category.replace('_', ' ')} profile. Candidate does not meet the core requirements."
                experience_match_str = experience_analysis["experience_match"]
                education_match_str = education_analysis["education_match"]
            else:
                skill_score = (len(matched_skills_set) / len(relevant_jd_skills) * 100) if relevant_jd_skills else 70.0
                experience_score = experience_analysis["match_score"] * 100
                education_score = education_analysis["match_score"] * 100
                project_score = project_analysis["match_score"] * 100

                overall_score = (
                    skill_score * self.config.skill_weight +
                    experience_score * self.config.experience_weight +
                    education_score * self.config.education_weight +
                    project_score * self.config.project_weight
                )

                decision = "Shortlisted" if overall_score >= self.config.shortlist_threshold else "Rejected"

                reasoning_steps.append(
                    f"Weighted score: skills={skill_score:.1f}%×{self.config.skill_weight}, "
                    f"experience={experience_score:.1f}%×{self.config.experience_weight}, "
                    f"education={education_score:.1f}%×{self.config.education_weight}, "
                    f"projects={project_score:.1f}%×{self.config.project_weight}. "
                    f"Overall: {overall_score:.1f}%. Threshold: {self.config.shortlist_threshold}%. "
                    f"Decision: {decision}."
                )

                # Human-readable reasoning summary
                skill_verdict = "strong skill alignment" if skill_score >= 70 else "partial skill match" if skill_score >= 40 else "weak skill match"
                exp_verdict = experience_analysis["experience_match"]
                edu_verdict = education_analysis["education_match"]
                
                project_names_str = ', '.join(project_names) if project_names else "no notable projects"
                proj_verdict = f"{projects_found} relevant project(s) found: {project_names_str}" if projects_found > 0 else "no notable projects detected"

                if decision == "Shortlisted":
                    reasoning = (
                        f"Candidate demonstrates {skill_verdict} with {len(matched_skills)} matched skill(s). "
                        f"{exp_verdict}. {edu_verdict}. {proj_verdict}. "
                        f"Overall score of {overall_score:.1f}% meets the {self.config.shortlist_threshold}% threshold."
                    )
                else:
                    reasons = []
                    if skill_score < 50:
                        reasons.append(f"insufficient skill coverage ({len(missing_skills)} missing skill(s))")
                    if experience_score < 50:
                        reasons.append("limited relevant experience")
                    if education_score < 50:
                        reasons.append("education does not meet requirements")
                    if project_score < 40:
                        reasons.append("insufficient project experience")
                    reason_str = "; ".join(reasons) if reasons else "overall score below threshold"
                    reasoning = (
                        f"Candidate was rejected due to: {reason_str}. "
                        f"Overall score {overall_score:.1f}% is below the required {self.config.shortlist_threshold}% threshold."
                    )

                experience_match_str = experience_analysis["experience_match"]
                education_match_str = education_analysis["education_match"]

            self.reasoning_logs[session_id] = reasoning_steps

            # ── Final strict JSON output ─────────────────────────────────
            result = {
                # ── Primary fields (assignment spec) ──
                "decision": decision,
                "match_percentage": round(overall_score, 1),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "experience_match": experience_match_str,
                "education_match": education_match_str,
                "reasoning": reasoning,

                # ── Extended fields (for richer frontend display) ──
                "session_id": session_id,
                "score": round(overall_score, 1),          # alias for frontend compatibility
                "similarity_score": round(experience_analysis.get("similarity_score", 0.5), 2),
                "explanation": reasoning,                   # alias for frontend compatibility
                "detailed_analysis": {
                    "category": {
                        "jd_category": jd_category,
                        "resume_category": resume_category,
                        "category_match": category_match
                    },
                    "score_breakdown": {
                        "skills": round(
                            (len(matched_skills_set) / len(relevant_jd_skills) * 100) if relevant_jd_skills else 70.0, 1
                        ) if category_match else 20.0,
                        "experience": round(experience_analysis["match_score"] * 100, 1),
                        "education": round(education_analysis["match_score"] * 100, 1),
                        "projects": round(project_analysis["match_score"] * 100, 1),
                    },
                    "reasoning_loop": reasoning_steps,
                    "experience": experience_analysis,
                    "education": education_analysis,
                    "projects": project_analysis,
                }
            }

            elapsed = time.time() - start_time
            logger.info(f"Analysis completed in {elapsed:.2f}s | Decision: {decision} | Score: {overall_score:.1f}%")
            return result

        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}", exc_info=True)
            return {
                "decision": "Error",
                "match_percentage": 0,
                "matched_skills": [],
                "missing_skills": [],
                "experience_match": "Analysis failed",
                "education_match": "Analysis failed",
                "reasoning": f"An error occurred during analysis: {str(e)}",
                "session_id": session_id,
                "score": 0,
                "similarity_score": 0,
                "explanation": f"Analysis error: {str(e)}",
                "detailed_analysis": {"reasoning_loop": reasoning_steps}
            }

    def get_reasoning_loop(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self.reasoning_logs:
            raise ValueError(f"Session {session_id} not found")
        return self.reasoning_logs[session_id]
    