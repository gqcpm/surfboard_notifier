"""
Test suite for surfboard-monitor package.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from surfboard_monitor import SurfboardMonitor


def test_surfboard_monitor_init():
    """Test SurfboardMonitor initialization."""
    monitor = SurfboardMonitor()
    assert monitor.config is not None
    assert monitor.scraper is not None
    assert monitor.notifier is not None
    assert monitor.classifier is not None


@patch('surfboard_monitor.core.monitor.logging.basicConfig')
def test_setup_logging_calls_basicConfig(mock_basic):
    monitor = SurfboardMonitor()
    monitor.setup_logging()
    mock_basic.assert_called_once()


@patch('surfboard_monitor.core.monitor.Notifier.notify_new_listing')
@patch('surfboard_monitor.core.monitor.GeminiClassifier.classify_listings')
@patch('surfboard_monitor.core.monitor.CraigslistScraper.get_new_listings')
def test_check_for_new_listings_flow(mock_get, mock_classify, mock_notify):
    monitor = SurfboardMonitor()

    # Raw listings present
    mock_get.return_value = [{'title': '9\'6 Longboard', 'price': '$600', 'location': 'San Diego'}]
    # After AI filtering keep one
    mock_classify.return_value = [{'title': "9'6 Longboard", 'price': '$600', 'location': 'San Diego'}]

    monitor.check_for_new_listings()

    mock_get.assert_called_once()
    mock_classify.assert_called_once()
    mock_notify.assert_called_once()


@patch('surfboard_monitor.core.monitor.GeminiClassifier.classify_listings', return_value=[])
@patch('surfboard_monitor.core.monitor.CraigslistScraper.get_new_listings', return_value=[{'title': 'whatever'}])
def test_check_for_new_listings_none_after_ai(mock_get, mock_classify):
    monitor = SurfboardMonitor()
    # Should not raise and should not notify when AI filters everything
    with patch.object(monitor.notifier, 'notify_new_listing') as mock_notify:
        monitor.check_for_new_listings()
        mock_notify.assert_not_called()


@patch('surfboard_monitor.core.monitor.CraigslistScraper.get_new_listings', return_value=[])
def test_check_for_new_listings_no_raw_listings(mock_get):
    """Covers lines 61 (no raw listings branch)."""
    monitor = SurfboardMonitor()
    # Should simply log and return without error
    monitor.check_for_new_listings()
    mock_get.assert_called_once()


@patch('surfboard_monitor.core.monitor.CraigslistScraper.get_new_listings', side_effect=Exception('scrape fail'))
def test_check_for_new_listings_exception_path(mock_get):
    """Covers lines 63-64 (exception caught)."""
    monitor = SurfboardMonitor()
    # Should not raise
    monitor.check_for_new_listings()
    mock_get.assert_called_once()


def test_run_exits_on_keyboard_interrupt():
    monitor = SurfboardMonitor()
    with patch.object(monitor, 'setup_logging'):
        with patch.object(monitor, 'check_for_new_listings'):
            class Every:
                @property
                def seconds(self):
                    return self
                def do(self, *_args, **_kwargs):
                    return None
            with patch('surfboard_monitor.core.monitor.schedule.every', return_value=Every()):
                with patch('surfboard_monitor.core.monitor.time.sleep', side_effect=KeyboardInterrupt()):
                    # Should exit cleanly on KeyboardInterrupt
                    monitor.run()


def test_run_logs_unexpected_exception_and_exits():
    monitor = SurfboardMonitor()
    with patch.object(monitor, 'setup_logging'):
        with patch.object(monitor, 'check_for_new_listings'):
            class Every:
                @property
                def seconds(self):
                    return self
                def do(self, *_args, **_kwargs):
                    return None
            with patch('surfboard_monitor.core.monitor.schedule.every', return_value=Every()):
                # Raise inside loop to hit lines 94-95
                with patch('surfboard_monitor.core.monitor.schedule.run_pending', side_effect=Exception('boom')):
                    with patch('surfboard_monitor.core.monitor.time.sleep'):
                        monitor.run()

if __name__ == "__main__":
    pytest.main([__file__])
