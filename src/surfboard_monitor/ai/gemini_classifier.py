"""
Gemini AI classifier for surfboard type detection.
"""

import logging
from google import genai
from google.genai import errors
from ..config import Config
from .prompts import CLASSIFICATION_PROMPT_TEMPLATE, LISTING_FORMAT_TEMPLATE

logger = logging.getLogger(__name__)

class GeminiClassifier:
    """AI classifier for filtering surfboard listings using Gemini AI."""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        
        if self.config.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=self.config.GEMINI_API_KEY)
                logger.info("Gemini AI classifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {e}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY not configured - AI filtering disabled")
    
    def classify_listings(self, listings):
        """Classify multiple surfboard listings in a single API call and return only longboards."""
        if not self.client or not self.config.ENABLE_GEMINI_FILTERING:
            logger.info("Gemini filtering disabled - returning empty list (no notifications)")
            return []
        
        if not listings:
            return listings
        
        try:
            # Build a comprehensive prompt with all listings
            listings_text = ""
            for i, listing in enumerate(listings, 1):
                listings_text += LISTING_FORMAT_TEMPLATE.format(
                    i=i,
                    title=listing.get('title', ''),
                    description=listing.get('description', ''),
                    price=listing.get('price', '')
                )
            
            # Format the classification prompt with listings
            prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
                listings_text=listings_text
            )
            
            logger.info(f"Classifying {len(listings)} listings in batch with Gemini AI")
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            # Parse the response
            classifications = response.text.strip().split('\n')
            filtered_listings = []
            
            for i, (listing, classification_line) in enumerate(zip(listings, classifications)):
                # Extract classification from the line (handle formats like "1. LONGBOARD" or just "LONGBOARD")
                classification = classification_line.split('.')[-1].strip().upper()
                
                title = listing.get('title', 'Unknown')
                logger.info(f"Gemini classification for '{title}': {classification}")
                
                # Additional safety checks for obvious non-surfboard items
                title_lower = title.lower()
                if any(keyword in title_lower for keyword in ['router', 'modem', 'wifi', 'wetsuit', 'shirt', 'clothing', 'rack', 'bag', 'paddleboard', 'sup']):
                    logger.info(f"❌ Filtering out (safety check): {title}")
                    continue
                
                # Safety check: filter out obvious shortboards by dimensions
                if any(dim in title_lower for dim in ["5'7", "5'8", "5'9", "5'10", "5'11", "6'0", "6'1", "6'2", "5'7\"", "5'8\"", "5'9\"", "5'10\"", "5'11\"", "6'0\"", "6'1\"", "6'2\""]):
                    logger.info(f"❌ Filtering out (safety check - shortboard dimensions): {title}")
                    continue
                
                # Special case: noserider boards should be kept (they are longboards)
                if 'noserider' in title_lower and classification == 'OTHER':
                    logger.info(f"✅ Override: Noserider board should be LONGBOARD: {title}")
                    classification = 'LONGBOARD'
                
                # Keep only longboard
                if classification in ['LONGBOARD']:
                    logger.info(f"✅ Keeping {classification}: {title}")
                    filtered_listings.append(listing)
                else:
                    logger.info(f"❌ Filtering out {classification}: {title}")
            
            logger.info(f"Batch classification: {len(listings)} -> {len(filtered_listings)} listings")
            return filtered_listings
            
        except errors.APIError as e:
            logger.error(f"Gemini API error: {e.code} - {e.message}")
            # If API error, return empty list to be safe (no notifications)
            logger.warning("Returning empty list due to API error - no notifications will be sent")
            return []
        except Exception as e:
            logger.error(f"Error in batch classification with Gemini: {e}")
            # If classification fails, return empty list to be safe (no notifications)
            logger.warning("Returning empty list due to classification error - no notifications will be sent")
            return []
