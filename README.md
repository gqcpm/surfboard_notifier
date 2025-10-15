# 🏄 Surfboard Monitor

A Python script that monitors Craigslist for new surfboard listings and uses Gemini AI to filter for midlength and longboard surfboards, sending notifications when matches are found.

Attempted to do it on marketplace and offerup, but ran into issues with bot detectors.

I created this script because I was tired of constantly monitoring Facebook marketplace and offerup for good deals on used boards, so I created this script to do it for me. The idea behind looking for "mov" in the description is that the script would catch posts where people are moving as I noticed that those ones are often a better deal because they are usually trying to just get rid of things as I had seen for that Rob Stewart 9'0 pristine condition, including fins, leash, board bag for $300 😭.

## Features

- 🔍 Monitors Craigslist for surfboard listings
- 🤖 AI-powered filtering with Gemini AI (midlength/longboard only)
- 🎯 Optional "mov" keyword filtering
- 🔔 Desktop notifications (macOS, Windows, Linux)
- 📧 Email notifications (optional)
- ⏰ Configurable check intervals
- 📝 Comprehensive logging
- 🛡️ Duplicate detection to avoid spam

## Installation

1. **Clone or download this project**
   ```bash
   cd to/your/file/path
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Gemini API key** (for AI filtering)
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key for configuration

4. **Install Chrome browser** (required for web scraping)
   - Download and install Chrome if not already installed
   - The script will automatically download ChromeDriver

5. **Configure settings**
   ```bash
   cp env_example.txt .env
   ```
   Edit `.env` file with your preferences:
   ```bash
   # Location settings
   LOCATION=San Diego, CA
   RADIUS=25
   
   # Price range
   MIN_PRICE=0
   MAX_PRICE=2000
   
   # Monitoring settings
   CHECK_INTERVAL=300  # 5 minutes
   MAX_RESULTS=50
   
   # Notification settings
   ENABLE_DESKTOP_NOTIFICATIONS=true
   ENABLE_EMAIL_NOTIFICATIONS=false
   
   # Gemini AI settings
   GEMINI_API_KEY=your_gemini_api_key_here
   ENABLE_GEMINI_FILTERING=true
   ```

## AI Processing

**Intelligent AI Filtering**: The system uses advanced batch processing with strict filtering:

- **Single API call**: All listings processed together for maximum efficiency
- **Strict classification**: Only 7-8ft midlength and 8ft+ longboard surfboards
- **Safety filters**: Additional keyword filtering for routers, wetsuits, clothing, etc.
- **Smart filtering**: 6ft boards, shortboards, and non-surfboard items are filtered out
- **Error handling**: Returns empty list if AI fails (no spam notifications)

## Usage

### Basic Usage
```bash
python surfboard_monitor.py
```

### With Custom Configuration
```bash
# Set environment variables
export LOCATION="Los Angeles, CA"
export CHECK_INTERVAL=600  # 10 minutes
python surfboard_monitor.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOCATION` | Your location for search | "San Diego, CA" |
| `RADIUS` | Search radius in miles | 25 |
| `MIN_PRICE` | Minimum price filter | 0 |
| `MAX_PRICE` | Maximum price filter | 2000 |
| `CHECK_INTERVAL` | Check interval in seconds | 300 (5 minutes) |
| `MAX_RESULTS` | Maximum results per search | 50 |
| `ENABLE_DESKTOP_NOTIFICATIONS` | Enable desktop notifications | true |
| `ENABLE_EMAIL_NOTIFICATIONS` | Enable email notifications | false |

### Email Configuration (Optional)

If you want email notifications, set these in your `.env` file:

```bash
ENABLE_EMAIL_NOTIFICATIONS=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=your_email@gmail.com
```

**Note**: For Gmail, you'll need to use an App Password, not your regular password.

## How It Works

1. **Search**: The script searches Facebook Marketplace and OfferUp for surfboard listings
2. **Filter**: Only listings containing "mov" in the title or description are considered
3. **Track**: Duplicate listings are filtered out using unique identifiers
4. **Notify**: New matches trigger desktop and/or email notifications
5. **Log**: All activity is logged to `surfboard_monitor.log`

## Search Terms

The script searches for these terms:
- "surfboard"
- "surf board" 
- "surfing board"

## Notification Examples

### Desktop Notification
```
🏄 New Surfboard Alert!
Found: Custom Surfboard with Mov
Price: $450
Location: San Diego, CA
```

### Email Notification
```
Subject: New Surfboard Listing: Custom Surfboard with Mov

New surfboard listing found with "mov" in description:

Title: Custom Surfboard with Mov
Price: $450
Location: San Diego, CA
Description: Description not available in preview
Platform: Facebook Marketplace
URL: https://facebook.com/marketplace/item/...
```

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver issues**
   - Make sure Chrome is installed
   - The script will automatically download ChromeDriver

2. **No notifications appearing**
   - Check if desktop notifications are enabled in your system settings
   - Verify the script is running (check the log file)

3. **Script stops unexpectedly**
   - Check the log file for error messages
   - Ensure you have a stable internet connection

4. **Too many notifications**
   - Increase the `CHECK_INTERVAL` to check less frequently
   - The script automatically filters duplicates

### Logs

Check the log file for detailed information:
```bash
tail -f surfboard_monitor.log
```

## Legal Notice

This script is for personal use only. Please respect the terms of service of Facebook Marketplace and OfferUp. The script includes delays between requests to be respectful to the platforms.

## Requirements

- Python 3.8+
- Chrome browser
- Internet connection
- macOS, Windows, or Linux

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `selenium` - Web automation
- `plyer` - Desktop notifications
- `schedule` - Task scheduling
- `python-dotenv` - Environment variables
- `lxml` - XML/HTML processing
- `fake-useragent` - User agent rotation
- `webdriver-manager` - ChromeDriver management
