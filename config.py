import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI")
    
    # Discovery Parameters
    DEFAULT_RADIUS = 5000  # 5km in meters
    MAX_RADIUS = 25000 # 25km
    
    # Crawler Parameters
    SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    CRAWL_TIMEOUT = 30 # seconds
    
    # Scoring Weights
    SCORE_WEBSITE = 3
    SCORE_EMAIL = 3
    SCORE_PHONE = 2
    SCORE_SOCIAL = 2
    
    @classmethod
    def validate(cls):
        """Validate critical environment variables."""
        if not cls.GOOGLE_MAPS_API_KEY:
            raise ValueError("GOOGLE_MAPS_API_KEY is not set in .env file.")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env file.")
