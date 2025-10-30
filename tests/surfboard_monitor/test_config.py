"""
Tests for Config module.
"""

import os
import pytest
from unittest.mock import patch
from surfboard_monitor import Config


class TestConfig:
    """Test suite for Config class."""
    
    def test_config_defaults(self):
        """Test that Config class reflects env or default values."""
        config = Config()
        assert config.SEARCH_TERMS == ["surfboard", "surf board", "surfing board"]
        assert config.DESCRIPTION_KEYWORD == "mov"
        # Expect from environment if set, otherwise default
        assert config.CHECK_INTERVAL == int(os.getenv("CHECK_INTERVAL", "300"))
        assert config.MAX_RESULTS == int(os.getenv("MAX_RESULTS", "50"))
        assert config.MIN_PRICE == int(os.getenv("MIN_PRICE", "0"))
        assert config.MAX_PRICE == int(os.getenv("MAX_PRICE", "2000"))
        assert config.RADIUS == int(os.getenv("RADIUS", "25"))
    
    def test_config_search_terms(self):
        """Test search terms configuration."""
        config = Config()
        assert isinstance(config.SEARCH_TERMS, list)
        assert len(config.SEARCH_TERMS) == 3
        assert "surfboard" in config.SEARCH_TERMS
    
    def test_config_notification_defaults(self):
        """Test notification configuration defaults."""
        config = Config()
        assert isinstance(config.ENABLE_DESKTOP_NOTIFICATIONS, bool)
        assert isinstance(config.ENABLE_EMAIL_NOTIFICATIONS, bool)
    
    def test_config_logging_defaults(self):
        """Test logging configuration defaults."""
        config = Config()
        assert isinstance(config.LOG_LEVEL, str)
        assert isinstance(config.LOG_FILE, str)
        assert isinstance(config.USER_AGENT, str)
        assert len(config.USER_AGENT) > 0
    
    def test_config_gemini_settings(self):
        """Test Gemini AI configuration."""
        config = Config()
        assert isinstance(config.GEMINI_API_KEY, str)
        assert isinstance(config.ENABLE_GEMINI_FILTERING, bool)
    
    def test_config_email_settings(self):
        """Test email configuration."""
        config = Config()
        assert isinstance(config.EMAIL_SMTP_SERVER, str)
        assert isinstance(config.EMAIL_SMTP_PORT, int)
        assert isinstance(config.EMAIL_USERNAME, str)
        assert isinstance(config.EMAIL_PASSWORD, str)
        assert isinstance(config.EMAIL_TO, str)
    
    def test_config_price_range(self):
        """Test price range configuration."""
        config = Config()
        assert config.MIN_PRICE >= 0
        assert config.MAX_PRICE >= config.MIN_PRICE
    
    def test_config_location_default(self):
        """Test location default value is a non-empty string."""
        config = Config()
        assert isinstance(config.LOCATION, str)
        assert len(config.LOCATION) > 0
