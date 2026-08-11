"""
analyzer.py
-----------
Resume analysis and scoring engine.
"""

import re
from models import Resume, Education, Experience, Skills, Projects
from utils import (
    clean_text, extract_dates, calculate_years_from_dates,
    count_bullet_points, extract_technologies, extract_achievements,
    get_current_year, percentage
)


class ResumeAnalyzer:
    """Analyzes resume text and scores each section."""
    
    def __init__(self):
        self.resume = None
        self.section_keywords = {
            "Education": ["education", "academic", "degree", "university", "college", "school"],
            "Experience": ["experience", "work", "employment", "career", "professional"],
            "Skills": ["skills", "technologies", "tools", "competencies", "expertise"],
            "Projects": ["projects", "portfolio", "personal projects", "side projects"]
        }
    
    def analyze(self, raw_text):
        """Main analysis pipeline."""
        self.resume = Resume(raw_text)
        
        # Step 1: Split into sections
        self._extract_sections(raw_text)
        
        # Step 2: Score each section
        self._score_education()
        self._score_experience()
        self._score_skills()
        self._score_projects()
        
        # Step 3: Calculate overall score
        self._calculate_overall_score()
        
        # Step 4: Generate ranking
        self._generate_ranking()
        
        # Step 5: Generate suggestions
        self._generate_suggestions()
        
        return self.resume
    
    def _extract_sections(self, text):
        """Split resume into sections."""
        lines = text.split('\n')
        current_section = "Header"
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if line is a section header
            section_found = self._identify_section(line_stripped)
            
            if section_found:
                if current_content:
                    self._save_section(current_section, '\n'.join(current_content))
                current_section = section_found
                current_content = []
            else:
                current_content.append(line_stripped)
        
        # Save last section
        if current_content:
            self._save_section(current_section, '\n'.join(current_content))
    
    def _identify_section(self, line):
        """Check if line is a section header."""
        line_clean = re.sub(r'[^\w\s]', '', line.lower()).strip()
        
        for section, keywords in self.section_keywords.items():
            for keyword in keywords:
                if keyword in line_clean:
                    return section
        return None
    
    def _save_section(self, name, content):
        """Create section object and add to resume."""
        if name == "Education":
            self.resume.add_section(Education(content))
        elif name == "Experience":
            self.resume.add_section(Experience(content))
        elif name == "Skills":
            self.resume.add_section(Skills(content))
        elif name == "Projects":
            self.resume.add_section(Projects(content))
    
    def _score_education(self):
        """Score education section."""
        section = self.resume.get_section("Education")
        if not section:
            return
        
        score = 0
        feedback = []
        content_lower = section.content.lower()
        
        # Check for degree keywords
        degrees = ['bachelor', 'master', 'phd', 'bsc', 'msc', 'bs', 'ms', 'b.s.', 'm.s.']
        for degree in degrees:
            if degree in content_lower:
                score += 20
                feedback.append(f"✅ Found {degree} degree")
                break
        else:
            feedback.append("⚠️ No degree mentioned")
        
        # Check for institution names
        institutions = ['university', 'college', 'institute', 'school']
        for inst in institutions:
            if inst in content_lower:
                score += 15
                feedback.append(f"✅ Institution mentioned ({inst})")
                break
        
        # Check for GPA
        gpa_pattern = r'\bgpa[:\s]*[3-4]\.\d\b'
        if re.search(gpa_pattern, content_lower):
            score += 15
            feedback.append("✅ GPA mentioned")
        
        # Check for dates
        dates = extract_dates(section.content)
        if dates:
            score += 10
            feedback.append(f"✅ Education dates found ({len(dates)} dates)")
        
        # Check for relevant coursework
        if 'coursework' in content_lower or 'courses' in content_lower:
            score += 10
            feedback.append("✅ Coursework listed")
        
        # Check for honors/awards
        honors = ['honors', 'dean\'s list', 'scholarship', 'award']
        for honor in honors:
            if honor in content_lower:
                score += 10
                feedback.append(f"✅ {honor.title()} mentioned")
                break
        
        section.score = min(score, 100)
        section.feedback = feedback
    
    def _score_experience(self):
        """Score experience section."""
        section = self.resume.get_section("Experience")
        if not section:
            return
        
        score = 0
        feedback = []
        content_lower = section.content.lower()
        
        # Calculate years of experience
        dates = extract_dates(section.content)
        years = calculate_years_from_dates(dates)
        
        if years >= 5:
            score += 25
            feedback.append(f"✅ Strong experience ({years} years)")
        elif years >= 2:
            score += 15
            feedback.append(f"✅ Good experience ({years} years)")
        elif years > 0:
            score += 10
            feedback.append(f"⚠️ Limited experience ({years} years)")
        else:
            feedback.append("⚠️ Could not determine years of experience")
        
        # Check for job titles
        titles = ['developer', 'engineer', 'manager', 'analyst', 'designer', 'lead', 'senior']
        title_count = sum(1 for title in titles if title in content_lower)
        if title_count > 0:
            score += 15
            feedback.append(f"✅ Job titles found ({title_count} mentions)")
        
        # Check for bullet points
        bullet_count = count_bullet_points(section.content)
        if bullet_count >= 5:
            score += 15
            feedback.append(f"✅ Good detail ({bullet_count} bullet points)")
        elif bullet_count > 0:
            score += 10
            feedback.append(f"⚠️ Limited detail ({bullet_count} bullet points)")
        else:
            feedback.append("⚠️ No bullet points for responsibilities")
        
        # Check for achievements
        achievements = extract_achievements(section.content)
        if len(achievements) >= 3:
            score += 15
            feedback.append(f"✅ Strong achievements ({len(achievements)} found)")
        elif achievements:
            score += 10
            feedback.append(f"✅ Some achievements ({len(achievements)} found)")
        else:
            feedback.append("⚠️ No quantifiable achievements found")
        
        # Check for action verbs
        action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'improved', 'designed']
        verb_count = sum(1 for verb in action_verbs if verb in content_lower)
        if verb_count >= 3:
            score += 10
            feedback.append("✅ Good use of action verbs")
        
        section.score = min(score, 100)
        section.feedback = feedback
    
    def _score_skills(self):
        """Score skills section."""
        section = self.resume.get_section("Skills")
        if not section:
            return
        
        score = 0
        feedback = []
        
        # Extract technologies
        technologies = extract_technologies(section.content)
        
        if len(technologies) >= 10:
            score += 40
            feedback.append(f"✅ Strong tech stack ({len(technologies)} technologies)")
        elif len(technologies) >= 5:
            score += 25
            feedback.append(f"✅ Good tech stack ({len(technologies)} technologies)")
        elif len(technologies) > 0:
            score += 15
            feedback.append(f"⚠️ Limited tech stack ({len(technologies)} technologies)")
        else:
            feedback.append("⚠️ No technologies listed")
        
        # Categorize skills
        programming = ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust']
        frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node']
        databases = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']
        cloud_devops = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd']
        
        tech_lower = [t.lower() for t in technologies]
        
        has_programming = any(p in tech_lower for p in programming)
        has_frameworks = any(f in tech_lower for f in frameworks)
        has_databases = any(d in tech_lower for d in databases)
        has_cloud = any(c in tech_lower for c in cloud_devops)
        
        if has_programming:
            score += 15
            feedback.append("✅ Programming languages listed")
        
        if has_frameworks:
            score += 15
            feedback.append("✅ Frameworks listed")
        
        if has_databases:
            score += 15
            feedback.append("✅ Database technologies listed")
        
        if has_cloud:
            score += 15
            feedback.append("✅ Cloud/DevOps skills listed")
        
        section.score = min(score, 100)
        section.feedback = feedback
        section.technologies = technologies
    
    def _score_projects(self):
        """Score projects section."""
        section = self.resume.get_section("Projects")
        if not section:
            return
        
        score = 0
        feedback = []
        
        # Count projects
        project_patterns = [
            r'project\s+\d+',
            r'^[•\-*]\s+\w+',
            r'#{1,3}\s+\w+'
        ]
        
        project_count = 0
        for pattern in project_patterns:
            matches = re.findall(pattern, section.content, re.MULTILINE | re.IGNORECASE)
            project_count += len(matches)
        
        if project_count >= 3:
            score += 30
            feedback.append(f"✅ Strong portfolio ({project_count} projects)")
        elif project_count >= 1:
            score += 20
            feedback.append(f"⚠️ Limited portfolio ({project_count} projects)")
        else:
            feedback.append("⚠️ No projects found")
        
        # Check for technologies
        technologies = extract_technologies(section.content)
        if technologies:
            score += 20
            feedback.append(f"✅ Technologies used: {', '.join(technologies[:5])}")
        
        # Check for GitHub links
        if 'github.com' in section.content.lower():
            score += 15
            feedback.append("✅ GitHub links provided")
        
        # Check for live demos
        if any(word in section.content.lower() for word in ['live', 'demo', 'deployed', 'production']):
            score += 15
            feedback.append("✅ Live demos mentioned")
        
        section.score = min(score, 100)
        section.feedback = feedback
    
    def _calculate_overall_score(self):
        """Calculate overall resume score."""
        scores = []
        weights = {
            "Experience": 0.35,
            "Skills": 0.25,
            "Projects": 0.25,
            "Education": 0.15
        }
        
        for section_name, weight in weights.items():
            section = self.resume.get_section(section_name)
            if section:
                scores.append(section.score * weight)
            else:
                scores.append(0)
        
        self.resume.overall_score = round(sum(scores))
    
    def _generate_ranking(self):
        """Generate overall ranking."""
        score = self.resume.overall_score
        
        if score >= 90:
            self.resume.ranking = "Excellent"
        elif score >= 80:
            self.resume.ranking = "Very Good"
        elif score >= 70:
            self.resume.ranking = "Good"
        elif score >= 60:
            self.resume.ranking = "Average"
        elif score >= 50:
            self.resume.ranking = "Below Average"
        else:
            self.resume.ranking = "Needs Improvement"
    
    def _generate_suggestions(self):
        """Generate improvement suggestions."""
        suggestions = []
        
        # Check for missing sections
        required_sections = ["Experience", "Skills", "Education", "Projects"]
        for section in required_sections:
            if section not in self.resume.sections:
                suggestions.append(f"Add a {section} section")
        
        # Score-based suggestions
        experience = self.resume.get_section("Experience")
        if experience and experience.score < 60:
            suggestions.append("Improve experience section with more bullet points and achievements")
        
        skills = self.resume.get_section("Skills")
        if skills and skills.score < 60:
            suggestions.append("Add more technical skills and categorize them")
        
        projects = self.resume.get_section("Projects")
        if projects and projects.score < 60:
            suggestions.append("Include more projects with GitHub links")
        
        education = self.resume.get_section("Education")
        if education and education.score < 60:
            suggestions.append("Add GPA, honors, or relevant coursework")
        
        # General suggestions
        if self.resume.overall_score < 70:
            suggestions.append("Add quantifiable achievements (e.g., 'Improved performance by 30%')")
            suggestions.append("Use action verbs (Led, Developed, Implemented)")
            suggestions.append("Keep resume to 1-2 pages")
        
        self.resume.suggestions = suggestions