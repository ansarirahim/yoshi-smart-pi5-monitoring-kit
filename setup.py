"""
Setup script for Raspberry Pi Smart Monitoring Kit.

Package configuration and installation script.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="rpi-smart-monitoring",
    version="0.1.0",
    author="A.R. Ansari",
    author_email="ansarirahim1@gmail.com",
    description="Raspberry Pi Smart Monitoring Kit for Wi-Fi Cameras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ansarirahim/raspberry-pi-smart-monitoring",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Home Automation",
    ],
    entry_points={
        "console_scripts": [
            "rpi-monitor=main:main",
        ],
    },
    keywords="raspberry-pi monitoring camera rtsp opencv detection",
)

