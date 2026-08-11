"""
models.py
---------
Data classes for resume sections.
"""


class Section:
    """Base class for all resume sections."""
    
    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.score = 0
        self.feedback = []
    
    def __repr__(self):
        return f"Section({self.name}, score={self.score})"


class Education(Section):
    """Education section data."""
    
    def __init__(self, content):
        super().__init__("Education", content)
        self.degrees = []
        self.institutions = []


class Experience(Section):
    """Work experience section data."""
    
    def __init__(self, content):
        super().__init__("Experience", content)
        self.years = 0
        self.companies = []
        self.achievements = []


class Skills(Section):
    """Skills section data."""
    
    def __init__(self, content):
        super().__init__("Skills", content)
        self.technical = []
        self.soft = []
        self.tools = []
        self.technologies = []


class Projects(Section):
    """Projects section data."""
    
    def __init__(self, content):
        super().__init__("Projects", content)
        self.project_count = 0
        self.technologies = []


class Resume:
    """Complete resume with all sections."""
    
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.sections = {}
        self.overall_score = 0
        self.ranking = "Not Ranked"
        self.suggestions = []
    
    def add_section(self, section):
        self.sections[section.name] = section
    
    def get_section(self, name):
        return self.sections.get(name)