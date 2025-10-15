#!/usr/bin/env python3
"""
Main script for monitoring surfboard listings on Facebook Marketplace and OfferUp.
"""

import logging
import time
import schedule
from datetime import datetime
from config import Config
from craigslist_scraper import CraigslistScraper
from notifier import Notifier
from gemini_classifier import GeminiClassifier

def setup_logging():
    """Setup logging configuration."""
    config = Config()
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def check_for_new_listings():
    """Check for new surfboard listings and send notifications."""
    logger = logging.getLogger(__name__)
    logger.info("Starting surfboard listing check...")
    
    try:
        scraper = CraigslistScraper()
        notifier = Notifier()
        classifier = GeminiClassifier()
        
        # Get new listings
        raw_listings = scraper.get_new_listings()
        
        if raw_listings:
            logger.info(f"Found {len(raw_listings)} raw surfboard listings")
            
            # Filter with Gemini AI for midlength/longboard
            new_listings = classifier.classify_listings(raw_listings)
            
            if new_listings:
                logger.info(f"After Gemini filtering: {len(new_listings)} longboard surfboards")
                
                for listing in new_listings:
                    logger.info(f"New listing: {listing.get('title', 'Unknown')} - {listing.get('price', 'N/A')}")
                    notifier.notify_new_listing(listing)
            else:
                logger.info("No longboard surfboards found after AI filtering")
                if Config().ENABLE_GEMINI_FILTERING:
                    logger.info("This is expected behavior - AI is working correctly to filter out non-longboard items")
        else:
            logger.info("No new surfboard listings found")
    
    except Exception as e:
        logger.error(f"Error during listing check: {e}")

def main():
    """Main function to run the surfboard monitor."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    config = Config()
    
    logger.info("🏄 Surfboard Monitor Started (Craigslist + Gemini AI)")
    logger.info(f"Search terms: {config.SEARCH_TERMS}")
    logger.info(f"Description keyword: {config.DESCRIPTION_KEYWORD}")
    logger.info(f"Location: {config.LOCATION}")
    logger.info(f"Check interval: {config.CHECK_INTERVAL} seconds")
    logger.info(f"Desktop notifications: {config.ENABLE_DESKTOP_NOTIFICATIONS}")
    logger.info(f"Email notifications: {config.ENABLE_EMAIL_NOTIFICATIONS}")
    logger.info(f"Gemini AI filtering: {config.ENABLE_GEMINI_FILTERING}")
    logger.info(f"Gemini API key configured: {'Yes' if config.GEMINI_API_KEY else 'No'}")
    
    # Run initial check
    check_for_new_listings()
    
    # Schedule regular checks
    schedule.every(config.CHECK_INTERVAL).seconds.do(check_for_new_listings)
    
    logger.info("Surfboard monitor is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Surfboard monitor stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
