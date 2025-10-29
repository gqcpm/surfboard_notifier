"""
Surfboard Monitor - A Python package for monitoring surfboard listings.

This package provides functionality to monitor Craigslist for new surfboard listings,
filter them using AI, and send notifications when matches are found.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.monitor import SurfboardMonitor
from .scrapers.craigslist_scraper import CraigslistScraper
from .ai.gemini_classifier import GeminiClassifier
from .notifications.notifier import Notifier
from .config import Config

__all__ = [
    "SurfboardMonitor",
    "CraigslistScraper", 
    "GeminiClassifier",
    "Notifier",
    "Config",
]
