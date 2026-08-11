"""
utils.py
--------
Helper functions for text processing.
"""

import re
from datetime import datetime


def clean_text(text):
    """Remove extra whitespace and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_dates(text):
    """Find all dates in text."""
    patterns = [
        r'\b(\d{4}-\d{2}-\d{2})\b',
        r'\b(\d{2}/\d{4})\b',
        r'\b(\d{4})\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}\b'
    ]
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    return dates


def calculate_years_from_dates(dates):
    """Estimate total years from date ranges."""
    years = []
    for date_str in dates:
        try:
            if isinstance(date_str, tuple):
                date_str = date_str[0]
            year = int(re.search(r'\d{4}', date_str).group())
            years.append(year)
        except:
            continue
    
    if len(years) >= 2:
        return max(years) - min(years)
    return 0


def count_bullet_points(text):
    """Count bullet points in text."""
    bullets = re.findall(r'[•\-\*]\s+', text)
    return len(bullets)


def extract_technologies(text):
    """Extract common tech keywords."""
    tech_keywords = [
        'python', 'java', 'javascript', 'js', 'ts', 'typescript',
        'react', 'angular', 'vue', 'node', 'nodejs', 'express',
        'django', 'flask', 'fastapi', 'spring', 'spring boot',
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'k8s',
        'git', 'github', 'gitlab', 'ci/cd', 'jenkins',
        'linux', 'bash', 'terraform', 'ansible',
        'html', 'css', 'sass', 'tailwind', 'bootstrap',
        'rest', 'graphql', 'api', 'microservices',
        'machine learning', 'ml', 'ai', 'deep learning',
        'tensorflow', 'pytorch', 'pandas', 'numpy'
    ]
    
    found = []
    text_lower = text.lower()
    for tech in tech_keywords:
        if tech in text_lower:
            found.append(tech)
    return list(set(found))


def extract_achievements(text):
    """Find achievement keywords."""
    patterns = [
        r'\b(\d+%)\b',
        r'\b(\$[\d,]+)\b',
        r'\b(increased|improved|reduced|saved|generated|launched|built|led|managed)\b'
    ]
    achievements = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        achievements.extend(matches)
    return achievements


def get_current_year():
    return datetime.now().year


def percentage(part, whole):
    """Calculate percentage safely."""
    if whole == 0:
        return 0
    return (part / whole) * 100