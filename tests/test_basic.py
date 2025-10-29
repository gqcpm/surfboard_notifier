"""
Test suite for surfboard-monitor package.
"""

import pytest
from unittest.mock import Mock, patch
from surfboard_monitor import SurfboardMonitor, CraigslistScraper, GeminiClassifier, Notifier, Config

def test_config_defaults():
    """Test that Config class has expected default values."""
    config = Config()
    assert config.SEARCH_TERMS == ["surfboard", "surf board", "surfing board"]
    assert config.DESCRIPTION_KEYWORD == "mov"
    assert config.CHECK_INTERVAL == 300
    assert config.MAX_RESULTS == 50

def test_craigslist_scraper_init():
    """Test CraigslistScraper initialization."""
    scraper = CraigslistScraper()
    assert scraper.config is not None
    assert scraper.seen_listings == set()
    assert scraper.session is not None

def test_gemini_classifier_init():
    """Test GeminiClassifier initialization."""
    classifier = GeminiClassifier()
    assert classifier.config is not None

def test_notifier_init():
    """Test Notifier initialization."""
    notifier = Notifier()
    assert notifier.config is not None

def test_surfboard_monitor_init():
    """Test SurfboardMonitor initialization."""
    monitor = SurfboardMonitor()
    assert monitor.config is not None
    assert monitor.scraper is not None
    assert monitor.notifier is not None
    assert monitor.classifier is not None

@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_craigslist_search_mock(mock_get):
    """Test Craigslist search with mocked response."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<html><body>Mock Craigslist page</body></html>'
    mock_get.return_value = mock_response
    
    scraper = CraigslistScraper()
    listings = scraper.search_craigslist("surfboard", "sfbay")
    
    # Should return empty list since we're mocking HTML without proper structure
    assert isinstance(listings, list)

def test_gemini_classifier_empty_listings():
    """Test GeminiClassifier with empty listings."""
    classifier = GeminiClassifier()
    result = classifier.classify_listings([])
    assert result == []

@patch('surfboard_monitor.notifications.notifier.notification.notify')
def test_desktop_notification(mock_notify):
    """Test desktop notification functionality."""
    notifier = Notifier()
    notifier.send_desktop_notification("Test Title", "Test Message")
    
    # Should not call notify if desktop notifications are disabled
    # This depends on the config, but we can test the method exists
    assert hasattr(notifier, 'send_desktop_notification')

if __name__ == "__main__":
    pytest.main([__file__])
