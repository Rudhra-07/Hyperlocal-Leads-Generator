import re
from typing import Optional

def normalize_string(text: str) -> str:
    """Normalize string for deduplication and comparison."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())

def calculate_lead_score(data: dict) -> int:
    """
    Calculate lead score based on available data.
    Signals:
    Website present → +3
    Email found → +3
    Phone found → +2
    Active social media profile → +2
    Total Max: 10
    """
    score = 0
    if data.get("website"):
        score += 3
    if data.get("email"):
        score += 3
    if data.get("phone"):
        score += 2
        
    # Check for social media links
    social_links = data.get("social_links", [])
    if isinstance(social_links, str):
        social_links = [social_links]
    
    if social_links and len(social_links) > 0:
        score += 2
        
    return score

def get_quality_tier(score: int) -> str:
    """Return quality tier based on score."""
    if score >= 6:
        return "High Quality"
    elif score >= 3:
        return "Standard"
    else:
        return "Low Priority"
