#!/bin/bash
# Installation script for Raspberry Pi Smart Monitoring Kit

set -e

echo "========================================="
echo "Raspberry Pi Smart Monitoring Kit"
echo "Installation Script"
echo "========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libopencv-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    i2c-tools \
    python3-smbus \
    git

# Enable I2C for servo control
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Create project directory
CURRENT_USER=$(whoami)
PROJECT_DIR="/home/${CURRENT_USER}/raspberry-pi-smart-monitoring"
echo "Creating project directory: $PROJECT_DIR"
mkdir -p $PROJECT_DIR

# If not already in project directory, navigate to it
if [ "$(pwd)" != "$PROJECT_DIR" ]; then
    echo "Note: Run this script from the project directory"
    echo "Current directory: $(pwd)"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p snapshots
mkdir -p config
mkdir -p assets

# Copy configuration files
echo "Setting up configuration..."
cp config/config.yaml config/config.yaml.backup
cp config/secrets.example.json config/secrets.json

# Set permissions
echo "Setting permissions..."
chmod +x scripts/*.sh
chmod 644 config/config.yaml
chmod 600 config/secrets.json

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/rpi-monitoring.service > /dev/null <<EOF
[Unit]
Description=Raspberry Pi Smart Monitoring Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml with your camera RTSP URL"
echo "2. Edit config/secrets.json with your LINE API credentials"
echo "3. Enable service: sudo systemctl enable rpi-monitoring"
echo "4. Start service: sudo systemctl start rpi-monitoring"
echo "5. Check status: sudo systemctl status rpi-monitoring"
echo ""
echo "For detailed setup instructions, see docs/manual/SETUP.md"

