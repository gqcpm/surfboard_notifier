"""
Marketplace scraping functionality for Facebook Marketplace and OfferUp.
"""

import requests
import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from config import Config

logger = logging.getLogger(__name__)

class MarketplaceScraper:
    def __init__(self):
        self.config = Config()
        self.ua = UserAgent()
        self.seen_listings = set()  # Track seen listings to avoid duplicates
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-agent={self.config.USER_AGENT}")
        
        try:
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return None
    
    def search_facebook_marketplace(self, search_term):
        """Search Facebook Marketplace for listings."""
        listings = []
        driver = self.setup_driver()
        
        if not driver:
            return listings
        
        try:
            # Navigate to Facebook Marketplace
            search_url = f"https://www.facebook.com/marketplace/search/?query={search_term}&sortBy=creation_time_desc"
            driver.get(search_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='marketplace_search_results']"))
            )
            
            # Scroll to load more results
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find listing elements
            listing_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='marketplace_search_results'] > div")
            
            for element in listing_elements[:self.config.MAX_RESULTS]:
                try:
                    listing = self._parse_facebook_listing(element)
                    if listing and self._contains_mov_keyword(listing):
                        listing['platform'] = 'Facebook Marketplace'
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse Facebook listing: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching Facebook Marketplace: {e}")
        
        finally:
            driver.quit()
        
        return listings
    
    def search_offerup(self, search_term):
        """Search OfferUp for listings."""
        listings = []
        driver = self.setup_driver()
        
        if not driver:
            return listings
        
        try:
            # Navigate to OfferUp
            search_url = f"https://offerup.com/search/?q={search_term}"
            driver.get(search_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search-results']"))
            )
            
            # Scroll to load more results
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find listing elements
            listing_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='search-results'] > div")
            
            for element in listing_elements[:self.config.MAX_RESULTS]:
                try:
                    listing = self._parse_offerup_listing(element)
                    if listing and self._contains_mov_keyword(listing):
                        listing['platform'] = 'OfferUp'
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse OfferUp listing: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching OfferUp: {e}")
        
        finally:
            driver.quit()
        
        return listings
    
    def _parse_facebook_listing(self, element):
        """Parse a Facebook Marketplace listing element."""
        listing = {}
        
        try:
            # Extract title
            title_element = element.find_element(By.CSS_SELECTOR, "span[dir='auto']")
            listing['title'] = title_element.text.strip()
            
            # Extract price
            try:
                price_element = element.find_element(By.CSS_SELECTOR, "span[dir='auto']:contains('$')")
                listing['price'] = price_element.text.strip()
            except:
                listing['price'] = 'Price not available'
            
            # Extract location
            try:
                location_element = element.find_element(By.CSS_SELECTOR, "span[dir='auto']:last-child")
                listing['location'] = location_element.text.strip()
            except:
                listing['location'] = 'Location not available'
            
            # Extract URL
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "a")
                listing['url'] = link_element.get_attribute('href')
            except:
                listing['url'] = 'URL not available'
            
            # Extract description (this might require clicking on the listing)
            listing['description'] = 'Description not available in preview'
            
            # Create unique ID for tracking
            listing['id'] = f"fb_{hash(listing.get('title', '') + listing.get('url', ''))}"
            
        except Exception as e:
            logger.warning(f"Failed to parse Facebook listing element: {e}")
            return None
        
        return listing
    
    def _parse_offerup_listing(self, element):
        """Parse an OfferUp listing element."""
        listing = {}
        
        try:
            # Extract title
            title_element = element.find_element(By.CSS_SELECTOR, "h3, h4, [data-testid='item-title']")
            listing['title'] = title_element.text.strip()
            
            # Extract price
            try:
                price_element = element.find_element(By.CSS_SELECTOR, "[data-testid='item-price'], .price")
                listing['price'] = price_element.text.strip()
            except:
                listing['price'] = 'Price not available'
            
            # Extract location
            try:
                location_element = element.find_element(By.CSS_SELECTOR, "[data-testid='item-location'], .location")
                listing['location'] = location_element.text.strip()
            except:
                listing['location'] = 'Location not available'
            
            # Extract URL
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "a")
                listing['url'] = link_element.get_attribute('href')
            except:
                listing['url'] = 'URL not available'
            
            # Extract description
            listing['description'] = 'Description not available in preview'
            
            # Create unique ID for tracking
            listing['id'] = f"ou_{hash(listing.get('title', '') + listing.get('url', ''))}"
            
        except Exception as e:
            logger.warning(f"Failed to parse OfferUp listing element: {e}")
            return None
        
        return listing
    
    def _contains_mov_keyword(self, listing):
        """Check if listing contains 'mov' keyword in title or description."""
        text_to_check = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        return 'mov' in text_to_check
    
    def get_new_listings(self):
        """Get new listings from all platforms."""
        all_listings = []
        
        for search_term in self.config.SEARCH_TERMS:
            logger.info(f"Searching for: {search_term}")
            
            # Search Facebook Marketplace
            fb_listings = self.search_facebook_marketplace(search_term)
            all_listings.extend(fb_listings)
            
            # Search OfferUp
            ou_listings = self.search_offerup(search_term)
            all_listings.extend(ou_listings)
            
            # Add delay between searches
            time.sleep(2)
        
        # Filter out seen listings
        new_listings = []
        for listing in all_listings:
            listing_id = listing.get('id')
            if listing_id and listing_id not in self.seen_listings:
                self.seen_listings.add(listing_id)
                new_listings.append(listing)
        
        return new_listings
