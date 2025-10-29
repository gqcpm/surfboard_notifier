# 🏄 Surfboard Monitor

A professional Python package that monitors Craigslist for new surfboard listings and uses Gemini AI to filter for midlength and longboard surfboards, sending notifications when matches are found.

## Background

This project was created to solve the problem of constantly monitoring marketplace websites for good surfboard deals. After missing out on several great deals that were gone within hours, I built this automated solution to stop the repetitive manual checking.

The AI filtering component addresses a key challenge: many surfboard listings have generic titles like "surfboard" without specifying the type (shortboard, midlength, longboard). This package uses Gemini AI to categorize boards by size and filter out irrelevant items like wetsuits, accessories, and other gear, ensuring you only get notified about boards that match your preferences.

## Features

- 🔍 Monitors Craigslist for surfboard listings
- 🤖 AI-powered filtering with Gemini AI (midlength/longboard only)
- 🎯 Optional keyword filtering
- 🔔 Desktop notifications (macOS, Windows, Linux)
- 📧 Email notifications (optional)
- ⏰ Configurable check intervals
- 📝 Comprehensive logging
- 🛡️ Duplicate detection to avoid spam
- 🏗️ Professional package structure with proper testing

## Installation

### Option 1: Install as Package (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/surfboard-monitor.git
   cd surfboard-monitor
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   ```

3. **Or install with development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

### Option 2: Direct Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run from source**
   ```bash
   python src/main.py
   ```

## Configuration

1. **Get Gemini API key** (for AI filtering)
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key for configuration

2. **Install Chrome browser** (required for web scraping)
   - Download and install Chrome if not already installed
   - The script will automatically download ChromeDriver

3. **Configure settings**
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

## Usage

### As a Package

```bash
# Run the monitor
surfboard-monitor

# Or using Python module
python -m surfboard_monitor
```

### As a Script

```bash
# Run the main script
python src/main.py

# Or run the legacy script
python scripts/legacy_surfboard_monitor.py
```

### Programmatic Usage

```python
from surfboard_monitor import SurfboardMonitor

# Create and run monitor
monitor = SurfboardMonitor()
monitor.run()
```

## Project Structure

```
surfboard-monitor/
├── src/
│   ├── surfboard_monitor/          # Main package
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── core/                  # Core monitoring functionality
│   │   │   ├── __init__.py
│   │   │   └── monitor.py         # Main monitor class
│   │   ├── scrapers/              # Web scraping modules
│   │   │   ├── __init__.py
│   │   │   └── craigslist_scraper.py
│   │   ├── ai/                    # AI classification
│   │   │   ├── __init__.py
│   │   │   └── gemini_classifier.py
│   │   └── notifications/         # Notification systems
│   │       ├── __init__.py
│   │       └── notifier.py
│   └── main.py                    # Entry point
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_basic.py
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── fixtures/                  # Test fixtures
├── scripts/                       # Utility scripts
│   └── legacy_surfboard_monitor.py
├── docs/                          # Documentation
├── requirements.txt               # Dependencies
├── setup.py                      # Package setup
├── pyproject.toml                 # Modern Python packaging
├── .gitignore                     # Git ignore rules
├── env_example.txt                # Environment template
└── README.md                      # This file
```

## AI Processing

**Intelligent AI Filtering**: The system uses advanced batch processing with strict filtering:

- **Single API call**: All listings processed together for maximum efficiency
- **Strict classification**: Only 7-8ft midlength and 8ft+ longboard surfboards
- **Safety filters**: Additional keyword filtering for routers, wetsuits, clothing, etc.
- **Smart filtering**: 6ft boards, shortboards, and non-surfboard items are filtered out
- **Error handling**: Returns empty list if AI fails (no spam notifications)

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/surfboard-monitor.git
cd surfboard-monitor

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=surfboard_monitor

# Run specific test file
pytest tests/test_basic.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
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

1. **Search**: The script searches Craigslist for surfboard listings
2. **Filter**: Only listings containing "mov" in the title or description are considered
3. **Track**: Duplicate listings are filtered out using unique identifiers
4. **Classify**: AI filters listings to only include longboards/midlengths
5. **Notify**: New matches trigger desktop and/or email notifications
6. **Log**: All activity is logged to `surfboard_monitor.log`

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
Platform: Craigslist
URL: https://sfbay.craigslist.org/...
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

This script is for personal use only. Please respect the terms of service of Craigslist. The script includes delays between requests to be respectful to the platforms.

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
- `google-genai` - Gemini AI integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release with professional package structure
- Craigslist scraping functionality
- Gemini AI integration for surfboard classification
- Desktop and email notifications
- Comprehensive logging and error handling
- Full test suite and development tools