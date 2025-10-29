#!/usr/bin/env python3
"""
Legacy script for running the surfboard monitor.
This is kept for backward compatibility.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from surfboard_monitor import SurfboardMonitor

def main():
    """Main function to run the surfboard monitor."""
    monitor = SurfboardMonitor()
    monitor.run()

if __name__ == "__main__":
    main()