import re
from typing import Dict, Any, List

class ProjectAnalyzer:
    """
    Analyzes project experience and relevance
    """
    
    def __init__(self):
        self.tech_stack_weights = {
            "web": ["react", "angular", "vue", "node", "django", "flask", "html", "css"],
            "mobile": ["android", "ios", "flutter", "react native", "kotlin", "swift"],
            "data": ["python", "sql", "pandas", "tensorflow", "pytorch", "tableau"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
            "devops": ["jenkins", "gitlab", "ci/cd", "ansible", "prometheus", "grafana"]
        }
    
    async def analyze(self, resume: str, jd: str) -> Dict[str, Any]:
        """
        Analyze project match between resume and job description
        """
        # Extract projects from resume
        resume_projects = await self._extract_projects(resume)
        
        # Extract project requirements from JD
        jd_project_req = await self._extract_project_requirements(jd)
        
        # Calculate match scores
        tech_stack_match = self._calculate_tech_stack_match(
            resume_projects["technologies"],
            jd_project_req["technologies"]
        )
        
        complexity_match = self._calculate_complexity_match(
            resume_projects["complexity_score"],
            jd_project_req["expected_complexity"]
        )
        
        relevance_match = self._calculate_relevance_match(
            resume_projects["descriptions"],
            jd_project_req["project_types"]
        )
        
        # Calculate overall match score
        weights = {"tech_stack": 0.5, "complexity": 0.25, "relevance": 0.25}
        overall_score = (
            tech_stack_match * weights["tech_stack"] +
            complexity_match * weights["complexity"] +
            relevance_match * weights["relevance"]
        )
        
        return {
            "match_score": round(overall_score, 2),
            "projects_count": resume_projects["count"],
            "technologies_used": resume_projects["technologies"][:10],
            "tech_stack_match": round(tech_stack_match * 100, 2),
            "complexity_score": resume_projects["complexity_score"],
            "details": {
                "projects": resume_projects["list"][:3],
                "required_tech": jd_project_req["technologies"][:5],
                "gaps": self._identify_tech_gaps(
                    resume_projects["technologies"],
                    jd_project_req["technologies"]
                )
            }
        }
    
    async def _extract_projects(self, text: str) -> Dict[str, Any]:
        """Extract project details from resume"""
        projects = {
            "count": 0,
            "technologies": set(),
            "descriptions": [],
            "list": [],
            "complexity_score": 0.0
        }
        
        # Find projects section
        project_section = self._find_projects_section(text)
        
        if project_section:
            # Split into individual projects
            project_entries = re.split(r'\n\s*(?=\w+[\s-]*:|\n)', project_section)
            
            for entry in project_entries:
                if len(entry.strip()) > 20:  # Minimum project description length
                    projects["count"] += 1
                    projects["descriptions"].append(entry)
                    
                    # Extract technologies
                    techs = await self._extract_technologies(entry)
                    projects["technologies"].update(techs)
                    
                    # Calculate complexity
                    complexity = self._calculate_project_complexity(entry)
                    projects["complexity_score"] = max(projects["complexity_score"], complexity)
                    
                    # Store project summary
                    projects["list"].append({
                        "description": entry[:100] + "...",
                        "technologies": list(techs),
                        "complexity": complexity
                    })
        
        return projects
    
    async def _extract_project_requirements(self, jd: str) -> Dict[str, Any]:
        """Extract project requirements from job description"""
        requirements = {
            "technologies": set(),
            "project_types": [],
            "expected_complexity": 0.7  # Default moderate-high complexity
        }
        
        # Extract technologies from requirements
        techs = await self._extract_technologies(jd)
        requirements["technologies"].update(techs)
        
        # Identify project types
        project_type_patterns = [
            r'(web|mobile|desktop|cloud).*?(application|platform|system)',
            r'(full.?stack|front.?end|back.?end).*?(development|project)',
            r'(data|analytics|machine learning).*?(pipeline|platform)'
        ]
        
        for pattern in project_type_patterns:
            matches = re.finditer(pattern, jd.lower())
            for match in matches:
                project_type = match.group()
                if project_type not in requirements["project_types"]:
                    requirements["project_types"].append(project_type)
        
        return requirements
    
    def _find_projects_section(self, text: str) -> str:
        """Find the projects section in resume"""
        patterns = [
            r'projects?(?:.*?)(?:\n\n|\Z)',
            r'professional projects?(?:.*?)(?:\n\n|\Z)',
            r'key projects?(?:.*?)(?:\n\n|\Z)',
            r'portfolio(?:.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group()
        
        return ""  # Return empty if no projects section found
    
    async def _extract_technologies(self, text: str) -> List[str]:
        """Extract technologies mentioned in text"""
        technologies = set()
        
        # Common technology keywords
        tech_keywords = [
            'react', 'angular', 'vue', 'node', 'python', 'java', 'c#', 'c++',
            'javascript', 'typescript', 'html', 'css', 'sql', 'mongodb',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'jenkins',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'flask', 'django',
            'spring', 'hibernate', 'jpa', 'rest', 'graphql', 'websocket'
        ]
        
        text_lower = text.lower()
        
        for tech in tech_keywords:
            if tech in text_lower:
                technologies.add(tech)
        
        return list(technologies)
    
    def _calculate_tech_stack_match(self, resume_techs: set, jd_techs: set) -> float:
        """Calculate technology stack match score"""
        if not jd_techs:
            return 0.5  # Neutral score if no tech specified
        
        matched = len(resume_techs & jd_techs)
        return matched / len(jd_techs)
    
    def _calculate_complexity_match(self, resume_complexity: float, expected_complexity: float) -> float:
        """Calculate project complexity match score"""
        if resume_complexity >= expected_complexity:
            return 1.0
        else:
            return resume_complexity / expected_complexity
    
    def _calculate_relevance_match(self, project_descs: List[str], project_types: List[str]) -> float:
        """Calculate project relevance match score"""
        if not project_types:
            return 0.5
        
        # Simplified relevance calculation
        relevance_score = 0.0
        for desc in project_descs:
            for ptype in project_types:
                if any(word in desc.lower() for word in ptype.split()):
                    relevance_score += 0.3
                    break
        
        return min(relevance_score, 1.0)
    
    def _calculate_project_complexity(self, project_desc: str) -> float:
        """Calculate complexity score for a project"""
        complexity = 0.3  # Base complexity
        
        # Indicators of higher complexity
        complexity_indicators = {
            'high': 0.3,
            'scale': 0.2,
            'distributed': 0.2,
            'microservices': 0.2,
            'real.time': 0.2,
            'optimization': 0.15,
            'architecture': 0.15,
            'designed': 0.1,
            'architected': 0.2,
            'led': 0.1,
            'team': 0.1,
            'multiple': 0.1
        }
        
        desc_lower = project_desc.lower()
        
        for indicator, value in complexity_indicators.items():
            if indicator in desc_lower:
                complexity += value
        
        return min(complexity, 1.0)
    
    def _identify_tech_gaps(self, resume_techs: set, required_techs: set) -> List[str]:
        """Identify technology gaps"""
        return list(required_techs - resume_techs)
    