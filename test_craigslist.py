#!/usr/bin/env python3
"""
Test script for Craigslist scraper.
"""

import logging
from craigslist_scraper import CraigslistScraper
from config import Config

def setup_logging():
    """Setup logging for testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_craigslist_scraper():
    """Test the Craigslist scraper."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    config = Config()
    
    logger.info("🏄 Testing Craigslist scraper for surfboard monitoring...")
    logger.info(f"Search terms: {config.SEARCH_TERMS}")
    logger.info(f"Description keyword: {config.DESCRIPTION_KEYWORD} (DISABLED FOR TESTING)")
    logger.info(f"Location: {config.LOCATION}")
    logger.info(f"Price range: ${config.MIN_PRICE} - ${config.MAX_PRICE}")
    
    try:
        # Initialize Craigslist scraper
        scraper = CraigslistScraper()
        
        # Test search
        logger.info("🔍 Testing Craigslist search...")
        listings = scraper.get_new_listings()
        
        if listings:
            logger.info(f"✅ Found {len(listings)} surfboard listings!")
            
            for i, listing in enumerate(listings[:5], 1):  # Show first 5
                logger.info(f"\n📋 Listing {i}:")
                logger.info(f"   Title: {listing.get('title', 'N/A')}")
                logger.info(f"   Price: {listing.get('price', 'N/A')}")
                logger.info(f"   Location: {listing.get('location', 'N/A')}")
                logger.info(f"   URL: {listing.get('url', 'N/A')}")
                logger.info(f"   Platform: {listing.get('platform', 'N/A')}")
        else:
            logger.info("ℹ️  No surfboard listings found")
            logger.info("This could mean:")
            logger.info("  - No surfboard listings posted today")
            logger.info("  - Search terms need adjustment")
            logger.info("  - Location mapping needs adjustment")
        
        logger.info("\n✅ Craigslist scraper test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Craigslist scraper test failed: {e}")
        return False

if __name__ == "__main__":
    test_craigslist_scraper()
