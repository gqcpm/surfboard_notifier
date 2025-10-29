#!/usr/bin/env python3
"""
Main entry point for the surfboard monitor application.
"""

from surfboard_monitor import SurfboardMonitor

def main():
    """Main function to run the surfboard monitor."""
    monitor = SurfboardMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
