"""
Tests for Notifier module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from surfboard_monitor import Notifier


class TestNotifier:
    """Test suite for Notifier class."""
    
    def test_notifier_init(self):
        """Test Notifier initialization."""
        notifier = Notifier()
        assert notifier.config is not None
    
    @patch('surfboard_monitor.notifications.notifier.notification.notify')
    def test_send_desktop_notification_enabled(self, mock_notify):
        """Test desktop notification when enabled."""
        notifier = Notifier()
        
        with patch.object(notifier.config, 'ENABLE_DESKTOP_NOTIFICATIONS', True):
            notifier.send_desktop_notification("Test Title", "Test Message")
            mock_notify.assert_called_once_with(
                title="Test Title",
                message="Test Message",
                timeout=10
            )
    
    @patch('surfboard_monitor.notifications.notifier.notification.notify')
    def test_send_desktop_notification_disabled(self, mock_notify):
        """Test desktop notification when disabled."""
        notifier = Notifier()
        
        with patch.object(notifier.config, 'ENABLE_DESKTOP_NOTIFICATIONS', False):
            notifier.send_desktop_notification("Test Title", "Test Message")
            mock_notify.assert_not_called()
    
    @patch('surfboard_monitor.notifications.notifier.notification.notify')
    def test_send_desktop_notification_error(self, mock_notify):
        """Test desktop notification error handling."""
        notifier = Notifier()
        mock_notify.side_effect = Exception("Notification error")
        
        with patch.object(notifier.config, 'ENABLE_DESKTOP_NOTIFICATIONS', True):
            # Should not raise exception
            notifier.send_desktop_notification("Test Title", "Test Message")
    
    @patch('surfboard_monitor.notifications.notifier.smtplib.SMTP')
    def test_send_email_notification_enabled(self, mock_smtp):
        """Test email notification when enabled."""
        notifier = Notifier()
        
        # Setup mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with patch.object(notifier.config, 'ENABLE_EMAIL_NOTIFICATIONS', True):
            with patch.object(notifier.config, 'EMAIL_USERNAME', 'test@example.com'):
                with patch.object(notifier.config, 'EMAIL_PASSWORD', 'password'):
                    with patch.object(notifier.config, 'EMAIL_TO', 'recipient@example.com'):
                        with patch.object(notifier.config, 'EMAIL_SMTP_SERVER', 'smtp.example.com'):
                            with patch.object(notifier.config, 'EMAIL_SMTP_PORT', 587):
                                notifier.send_email_notification(
                                    "Test Subject",
                                    "Test Body",
                                    "https://example.com"
                                )
                                
                                mock_smtp.assert_called_once_with('smtp.example.com', 587)
                                mock_server.starttls.assert_called_once()
                                mock_server.login.assert_called_once_with('test@example.com', 'password')
                                mock_server.sendmail.assert_called_once()
                                mock_server.quit.assert_called_once()
    
    def test_send_email_notification_disabled(self):
        """Test email notification when disabled."""
        notifier = Notifier()
        
        with patch.object(notifier.config, 'ENABLE_EMAIL_NOTIFICATIONS', False):
            with patch('surfboard_monitor.notifications.notifier.smtplib.SMTP') as mock_smtp:
                notifier.send_email_notification("Test Subject", "Test Body")
                mock_smtp.assert_not_called()
    
    def test_send_email_notification_missing_credentials(self):
        """Test email notification with missing credentials."""
        notifier = Notifier()
        
        with patch.object(notifier.config, 'ENABLE_EMAIL_NOTIFICATIONS', True):
            with patch.object(notifier.config, 'EMAIL_USERNAME', ''):
                with patch('surfboard_monitor.notifications.notifier.smtplib.SMTP') as mock_smtp:
                    notifier.send_email_notification("Test Subject", "Test Body")
                    mock_smtp.assert_not_called()
    
    @patch.object(Notifier, 'send_desktop_notification')
    @patch.object(Notifier, 'send_email_notification')
    def test_notify_new_listing(self, mock_email, mock_desktop):
        """Test notify_new_listing method."""
        notifier = Notifier()
        
        listing = {
            'title': 'Test Surfboard',
            'price': '$500',
            'location': 'San Diego, CA',
            'description': 'Great board',
            'platform': 'Craigslist',
            'url': 'https://example.com'
        }
        
        notifier.notify_new_listing(listing)
        
        # Verify desktop notification was called
        mock_desktop.assert_called_once()
        call_args = mock_desktop.call_args
        assert '🏄 New Surfboard Alert!' in call_args[0][0]
        assert 'Test Surfboard' in call_args[0][1]
        
        # Verify email notification was called
        mock_email.assert_called_once()
        email_args = mock_email.call_args
        assert 'Test Surfboard' in email_args[0][0]  # subject
        assert 'Test Surfboard' in email_args[0][1]  # body

    @patch('surfboard_monitor.notifications.notifier.smtplib.SMTP')
    def test_send_email_notification_error_path(self, mock_smtp):
        """Force SMTP error to cover exception branch."""
        notifier = Notifier()
        mock_smtp.side_effect = Exception('SMTP connect error')
        with patch.object(notifier.config, 'ENABLE_EMAIL_NOTIFICATIONS', True):
            with patch.object(notifier.config, 'EMAIL_USERNAME', 'x'):
                with patch.object(notifier.config, 'EMAIL_PASSWORD', 'y'):
                    with patch.object(notifier.config, 'EMAIL_TO', 'z'):
                        # Should not raise on exception
                        notifier.send_email_notification('s', 'b')
