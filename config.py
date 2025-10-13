"""
Configuration settings for the surfboard notification system.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Search parameters
    SEARCH_TERMS = ["surfboard", "surf board", "surfing board"]
    DESCRIPTION_KEYWORD = "mov"  # Must contain this word in description
    LOCATION = os.getenv("LOCATION", "San Diego, CA")  # Default location
    RADIUS = int(os.getenv("RADIUS", "25"))  # Search radius in miles
    
    # Price range
    MIN_PRICE = int(os.getenv("MIN_PRICE", "0"))
    MAX_PRICE = int(os.getenv("MAX_PRICE", "2000"))
    
    # Monitoring settings
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # 5 minutes in seconds
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "50"))
    
    # Notification settings
    ENABLE_DESKTOP_NOTIFICATIONS = os.getenv("ENABLE_DESKTOP_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    
    # Email settings (if enabled)
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_TO = os.getenv("EMAIL_TO", "")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "surfboard_monitor.log")
    
    # User agent for web scraping
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
