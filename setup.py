#!/usr/bin/env python3
"""
Setup script for surfboard-monitor package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="surfboard-monitor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for monitoring surfboard listings with AI filtering",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/surfboard-monitor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "surfboard-monitor=surfboard_monitor.core.monitor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
