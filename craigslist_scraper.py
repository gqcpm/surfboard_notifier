"""
Craigslist scraping functionality for surfboard monitoring.
"""

import requests
import time
import logging
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode
from config import Config

logger = logging.getLogger(__name__)

class CraigslistScraper:
    def __init__(self):
        self.config = Config()
        self.seen_listings = set()  # Track seen listings to avoid duplicates
        self.last_check_file = 'last_check_timestamp.json'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _get_last_check_time(self):
        """Get the timestamp of the last check, or 2 weeks ago if first run."""
        if os.path.exists(self.last_check_file):
            try:
                with open(self.last_check_file, 'r') as f:
                    data = json.load(f)
                    last_check = datetime.fromisoformat(data['last_check'])
                    logger.info(f"Last check was at: {last_check}")
                    return last_check
            except Exception as e:
                logger.warning(f"Error reading last check time: {e}")
        
        # First run: check last 2 weeks
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        logger.info(f"First run: checking listings from 2 weeks ago: {two_weeks_ago}")
        return two_weeks_ago
    
    def _save_check_time(self):
        """Save the current check time."""
        try:
            with open(self.last_check_file, 'w') as f:
                json.dump({'last_check': datetime.now().isoformat()}, f)
            logger.info(f"Saved check time: {datetime.now()}")
        except Exception as e:
            logger.error(f"Error saving check time: {e}")
    
    def _filter_listings_by_time(self, listings, cutoff_time):
        """Filter listings to only include those newer than cutoff_time."""
        filtered_listings = []
        
        for listing in listings:
            try:
                # Parse the date from the listing
                date_str = listing.get('date', '')
                if not date_str:
                    continue
                
                # Handle different date formats from Craigslist
                listing_date = None
                try:
                    # Try parsing common Craigslist date formats
                    if 'T' in date_str:
                        # ISO format: 2024-01-15T10:30:00-08:00
                        listing_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        # Try other formats
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y %H:%M']:
                            try:
                                listing_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                    
                    if listing_date and listing_date > cutoff_time:
                        filtered_listings.append(listing)
                        logger.debug(f"✅ Listing within time range: {listing.get('title', 'Unknown')} - {listing_date}")
                    else:
                        logger.debug(f"❌ Listing too old: {listing.get('title', 'Unknown')} - {listing_date}")
                        
                except Exception as e:
                    logger.warning(f"Error parsing date for listing {listing.get('title', 'Unknown')}: {e}")
                    # If we can't parse the date, include it to be safe
                    filtered_listings.append(listing)
            except Exception as e:
                logger.warning(f"Error processing listing {listing.get('title', 'Unknown')}: {e}")
                # If we can't process the listing, include it to be safe
                filtered_listings.append(listing)
        
        logger.info(f"Time filtering: {len(listings)} -> {len(filtered_listings)} listings")
        return filtered_listings
    
    def search_craigslist(self, search_term, location="sfbay"):
        """Search Craigslist for listings."""
        listings = []
        
        try:
            # Craigslist search URL
            base_url = f"https://{location}.craigslist.org"
            search_url = f"{base_url}/search/sss"
            
            params = {
                'query': search_term,
                'sort': 'date',  # Sort by newest first
                'hasPic': '1',  # Only posts with pictures
            }
            
            # Add price filter if configured
            if self.config.MIN_PRICE > 0:
                params['min_price'] = str(self.config.MIN_PRICE)
            if self.config.MAX_PRICE > 0:
                params['max_price'] = str(self.config.MAX_PRICE)
            
            full_url = f"{search_url}?{urlencode(params)}"
            logger.info(f"Searching Craigslist: {full_url}")
            
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Check what we actually got
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content length: {len(response.content)}")
            
            # Craigslist uses JSON-LD structured data, not traditional HTML elements
            # Look for the JSON-LD script tag with search results
            json_script = soup.find('script', {'id': 'ld_searchpage_results'})
            
            if json_script:
                import json
                try:
                    json_data = json.loads(json_script.string)
                    items = json_data.get('itemListElement', [])
                    logger.info(f"Found {len(items)} listings in JSON-LD data")
                    
                    # Convert JSON items to our format
                    for item_data in items[:self.config.MAX_RESULTS]:
                        try:
                            listing = self._parse_craigslist_json_item(item_data, base_url)
                            if listing:  # Remove mov filter for testing
                                listing['platform'] = 'Craigslist'
                                listings.append(listing)
                        except Exception as e:
                            logger.warning(f"Failed to parse JSON item: {e}")
                            continue
                    
                    return listings
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON-LD data: {e}")
            else:
                logger.warning("No JSON-LD data found in response")
            
            # Fallback to traditional HTML parsing if JSON-LD fails
            listing_elements = soup.find_all('li', class_='cl-search-result')
            if not listing_elements:
                listing_elements = soup.find_all('li', class_='result-row')
            if not listing_elements:
                listing_elements = soup.find_all('div', class_='result-info')
            
            logger.info(f"Found {len(listing_elements)} HTML listing elements")
            
            for element in listing_elements[:self.config.MAX_RESULTS]:
                try:
                    listing = self._parse_craigslist_listing(element, base_url)
                    if listing:  # Remove mov filter for testing
                        listing['platform'] = 'Craigslist'
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse Craigslist listing: {e}")
                    continue
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Craigslist: {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching Craigslist: {e}")
        
        return listings
    
    def _parse_craigslist_json_item(self, item_data, base_url):
        """Parse a Craigslist JSON-LD item into our standard format."""
        try:
            item = item_data.get('item', {})
            
            listing = {
                'id': f"cl_{hash(item.get('name', '') + str(item.get('offers', {}).get('price', '')))}",
                'title': item.get('name', 'No title'),
                'price': f"${item.get('offers', {}).get('price', 'N/A')}",
                'location': self._get_json_location(item),
                'url': '',  # JSON-LD doesn't include URLs
                'description': item.get('description', ''),
                'image_url': self._get_json_image(item),
                'condition': 'Unknown',
                'seller': 'Unknown',
                'listing_type': 'Unknown'
            }
            
            return listing
            
        except Exception as e:
            logger.warning(f"Failed to parse JSON item: {e}")
            return None
    
    def _get_json_location(self, item):
        """Extract location from JSON item."""
        try:
            offers = item.get('offers', {})
            available_at = offers.get('availableAtOrFrom', {})
            address = available_at.get('address', {})
            
            city = address.get('addressLocality', '')
            state = address.get('addressRegion', '')
            
            if city and state:
                return f"{city}, {state}"
            elif city:
                return city
            else:
                return 'Location not available'
        except:
            return 'Location not available'
    
    def _get_json_image(self, item):
        """Extract image URL from JSON item."""
        try:
            images = item.get('image', [])
            if images and len(images) > 0:
                return images[0]  # Return first image
            return ''
        except:
            return ''
    
    def _parse_craigslist_listing(self, element, base_url):
        """Parse a Craigslist listing element."""
        listing = {}
        
        try:
            # Extract title and URL
            title_link = element.find('a', class_='cl-app-anchor')
            if title_link:
                listing['title'] = title_link.get_text(strip=True)
                listing['url'] = urljoin(base_url, title_link.get('href', ''))
            else:
                listing['title'] = 'No title'
                listing['url'] = ''
            
            # Extract price
            price_elem = element.find('span', class_='priceinfo')
            if price_elem:
                listing['price'] = price_elem.get_text(strip=True)
            else:
                listing['price'] = 'Price not available'
            
            # Extract location
            location_elem = element.find('span', class_='meta')
            if location_elem:
                listing['location'] = location_elem.get_text(strip=True)
            else:
                listing['location'] = 'Location not available'
            
            # Extract description (from title for now, full description would require visiting each listing)
            listing['description'] = listing.get('title', '')
            
            # Extract image URL
            img_elem = element.find('img')
            if img_elem:
                listing['image_url'] = img_elem.get('src', '')
            else:
                listing['image_url'] = ''
            
            # Create unique ID for tracking
            listing['id'] = f"cl_{hash(listing.get('title', '') + listing.get('url', ''))}"
            
        except Exception as e:
            logger.warning(f"Failed to parse Craigslist listing element: {e}")
            return None
        
        return listing
    
    def _contains_mov_keyword(self, listing):
        """Check if listing contains 'mov' keyword in title or description."""
        text_to_check = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        return 'mov' in text_to_check
    
    def get_new_listings(self):
        """Get new listings from Craigslist for all search terms."""
        # Get the cutoff time for filtering
        cutoff_time = self._get_last_check_time()
        
        all_listings = []
        
        # Map location to Craigslist subdomain
        location_map = {
            'San Francisco': 'sfbay',
            'Los Angeles': 'losangeles', 
            'San Diego': 'sandiego',
            'New York': 'newyork',
            'Chicago': 'chicago',
            'Boston': 'boston',
            'Seattle': 'seattle',
            'Portland': 'portland',
            'Miami': 'miami',
            'Austin': 'austin',
            'Denver': 'denver',
            'Phoenix': 'phoenix',
            'Las Vegas': 'vegas',
            'Atlanta': 'atlanta',
            'Dallas': 'dallas',
            'Houston': 'houston',
            'Detroit': 'detroit',
            'Minneapolis': 'minneapolis',
            'Philadelphia': 'philadelphia',
            'Washington': 'washingtondc'
        }
        
        # Extract city from location
        location_city = self.config.LOCATION.split(',')[0].strip()
        craigslist_location = location_map.get(location_city, 'sfbay')  # Default to SF Bay Area
        
        for search_term in self.config.SEARCH_TERMS:
            logger.info(f"Searching Craigslist for: {search_term}")
            
            listings = self.search_craigslist(search_term, craigslist_location)
            all_listings.extend(listings)
            
            # Add delay between searches to be respectful
            time.sleep(2)
        
        # Filter listings by time (only get listings newer than last check)
        time_filtered_listings = self._filter_listings_by_time(all_listings, cutoff_time)
        
        # Filter out seen listings
        new_listings = []
        for listing in time_filtered_listings:
            listing_id = listing.get('id')
            if listing_id and listing_id not in self.seen_listings:
                self.seen_listings.add(listing_id)
                new_listings.append(listing)
        
        # Save the current check time
        self._save_check_time()
        
        logger.info(f"Found {len(new_listings)} new listings since last check")
        return new_listings
