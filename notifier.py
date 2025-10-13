"""
Notification system for surfboard alerts.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from plyer import notification
from config import Config

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self):
        self.config = Config()
    
    def send_desktop_notification(self, title, message):
        """Send desktop notification."""
        if not self.config.ENABLE_DESKTOP_NOTIFICATIONS:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            logger.info(f"Desktop notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
    
    def send_email_notification(self, subject, body, listing_url=None):
        """Send email notification."""
        if not self.config.ENABLE_EMAIL_NOTIFICATIONS:
            return
        
        if not all([self.config.EMAIL_USERNAME, self.config.EMAIL_PASSWORD, self.config.EMAIL_TO]):
            logger.warning("Email notifications enabled but credentials not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USERNAME
            msg['To'] = self.config.EMAIL_TO
            msg['Subject'] = subject
            
            # Add listing URL to body if provided
            if listing_url:
                body += f"\n\nView listing: {listing_url}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.EMAIL_SMTP_SERVER, self.config.EMAIL_SMTP_PORT)
            server.starttls()
            server.login(self.config.EMAIL_USERNAME, self.config.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(self.config.EMAIL_USERNAME, self.config.EMAIL_TO, text)
            server.quit()
            
            logger.info(f"Email notification sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def notify_new_listing(self, listing):
        """Send notification for a new surfboard listing."""
        title = f"🏄 New Surfboard Alert!"
        message = f"Found: {listing.get('title', 'Unknown')}\nPrice: {listing.get('price', 'N/A')}\nLocation: {listing.get('location', 'Unknown')}"
        
        # Send desktop notification
        self.send_desktop_notification(title, message)
        
        # Send email notification
        email_subject = f"New Surfboard Listing: {listing.get('title', 'Unknown')}"
        email_body = f"""
New surfboard listing found with "mov" in description:

Title: {listing.get('title', 'Unknown')}
Price: {listing.get('price', 'N/A')}
Location: {listing.get('location', 'Unknown')}
Description: {listing.get('description', 'No description available')}
Platform: {listing.get('platform', 'Unknown')}
URL: {listing.get('url', 'No URL available')}
        """
        
        self.send_email_notification(email_subject, email_body, listing.get('url'))
