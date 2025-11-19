#!/bin/bash
# Script to create SD card image for distribution

set -e

echo "========================================="
echo "Creating SD Card Image"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Configuration
IMAGE_NAME="rpi-smart-monitoring-v1.0.img"
MOUNT_POINT="/mnt/rpi-image"
IMAGE_SIZE="4G"

# Get SD card device
echo "Available devices:"
lsblk
echo ""
read -p "Enter SD card device (e.g., /dev/sdb): " SD_DEVICE

if [ ! -b "$SD_DEVICE" ]; then
    echo "Error: $SD_DEVICE is not a valid block device"
    exit 1
fi

# Confirm
echo ""
echo "WARNING: This will create an image from $SD_DEVICE"
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted"
    exit 1
fi

# Create image
echo "Creating image (this may take 10-20 minutes)..."
dd if=$SD_DEVICE of=$IMAGE_NAME bs=4M status=progress

# Shrink image (optional)
echo "Shrinking image..."
pishrink.sh $IMAGE_NAME

# Compress image
echo "Compressing image..."
gzip -9 $IMAGE_NAME

echo "========================================="
echo "Image created: ${IMAGE_NAME}.gz"
echo "========================================="
echo ""
echo "You can now distribute this image file"
echo "Users can flash it using Raspberry Pi Imager or balenaEtcher"

