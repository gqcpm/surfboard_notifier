"""
Main surfboard monitoring functionality.
"""

import logging
import time
import schedule
from datetime import datetime
from ..config import Config
from ..scrapers.craigslist_scraper import CraigslistScraper
from ..notifications.notifier import Notifier
from ..ai.gemini_classifier import GeminiClassifier

logger = logging.getLogger(__name__)

class SurfboardMonitor:
    """Main class for monitoring surfboard listings."""
    
    def __init__(self):
        self.config = Config()
        self.scraper = CraigslistScraper()
        self.notifier = Notifier()
        self.classifier = GeminiClassifier()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def check_for_new_listings(self):
        """Check for new surfboard listings and send notifications."""
        logger.info("Starting surfboard listing check...")
        
        try:
            # Get new listings
            raw_listings = self.scraper.get_new_listings()
            
            if raw_listings:
                logger.info(f"Found {len(raw_listings)} raw surfboard listings")
                
                # Filter with Gemini AI for midlength/longboard
                new_listings = self.classifier.classify_listings(raw_listings)
                
                if new_listings:
                    logger.info(f"After Gemini filtering: {len(new_listings)} longboard surfboards")
                    
                    for listing in new_listings:
                        logger.info(f"New listing: {listing.get('title', 'Unknown')} - {listing.get('price', 'N/A')}")
                        self.notifier.notify_new_listing(listing)
                else:
                    logger.info("No longboard surfboards found after AI filtering")
                    if self.config.ENABLE_GEMINI_FILTERING:
                        logger.info("This is expected behavior - AI is working correctly to filter out non-longboard items")
            else:
                logger.info("No new surfboard listings found")
        
        except Exception as e:
            logger.error(f"Error during listing check: {e}")
    
    def run(self):
        """Run the surfboard monitor."""
        self.setup_logging()
        
        logger.info("🏄 Surfboard Monitor Started (Craigslist + Gemini AI)")
        logger.info(f"Search terms: {self.config.SEARCH_TERMS}")
        logger.info(f"Description keyword: {self.config.DESCRIPTION_KEYWORD}")
        logger.info(f"Location: {self.config.LOCATION}")
        logger.info(f"Check interval: {self.config.CHECK_INTERVAL} seconds")
        logger.info(f"Desktop notifications: {self.config.ENABLE_DESKTOP_NOTIFICATIONS}")
        logger.info(f"Email notifications: {self.config.ENABLE_EMAIL_NOTIFICATIONS}")
        logger.info(f"Gemini AI filtering: {self.config.ENABLE_GEMINI_FILTERING}")
        logger.info(f"Gemini API key configured: {'Yes' if self.config.GEMINI_API_KEY else 'No'}")
        
        # Run initial check
        self.check_for_new_listings()
        
        # Schedule regular checks
        schedule.every(self.config.CHECK_INTERVAL).seconds.do(self.check_for_new_listings)
        
        logger.info("Surfboard monitor is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Surfboard monitor stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
