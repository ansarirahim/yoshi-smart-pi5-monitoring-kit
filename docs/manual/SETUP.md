# Raspberry Pi Smart Monitoring Kit - Setup Manual

## Hardware Requirements

### Required Components
- Raspberry Pi 4 (4GB RAM recommended)
- Official Raspberry Pi 4 Power Supply (5V/3A)
- MicroSD Card (32GB or 64GB, Class 10)
- Micro HDMI to HDMI cable
- USB Keyboard and Mouse (for initial setup)
- Wi-Fi Camera with RTSP support (ImCam Pro / ICSee compatible)

### Optional Components (for Pan-Tilt)
- 2x SG90 or MG90S Servo Motors
- PCA9685 16-Channel Servo Driver
- Pan-Tilt Servo Bracket
- 5V 2A Power Supply for Servos
- Jumper Wires (Male-Female)

### Optional Components (for Voice Alerts)
- Speaker or Audio Output Device
- 3.5mm Audio Cable

## Software Requirements

- Raspberry Pi OS (Debian-based, 64-bit recommended)
- Python 3.9 or higher
- OpenCV 4.x
- Internet connection for initial setup and OTA updates

## Installation Steps

### 1. Flash SD Card

1. Download the provided `.img` file
2. Use Raspberry Pi Imager or balenaEtcher
3. Flash the image to your microSD card
4. Insert the SD card into Raspberry Pi 4

### 2. Initial Boot

1. Connect HDMI cable to monitor
2. Connect keyboard and mouse
3. Connect power supply
4. Wait for system to boot (first boot may take 2-3 minutes)

### 3. Network Configuration

#### Wi-Fi Setup
```bash
sudo raspi-config
# Navigate to: System Options > Wireless LAN
# Enter your Wi-Fi SSID and password
```

#### Static IP (Optional but Recommended)
```bash
sudo nano /etc/dhcpcd.conf
```

Add the following lines:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

Reboot:
```bash
sudo reboot
```

### 4. Camera Configuration

1. Find your camera's RTSP URL
   - Usually: `rtsp://username:password@camera_ip:554/stream`
   - Check camera manual or ICSee app settings

2. Edit configuration file:
```bash
sudo nano /home/pi/rpi-monitoring/config/config.yaml
```

3. Update camera settings:
```yaml
camera:
  rtsp_url: "rtsp://admin:password@192.168.1.200:554/stream"
  username: "admin"
  password: "your_password"
```

### 5. LINE Messaging API Setup

1. Create LINE Messaging API Channel:
   - Visit: https://developers.line.biz/
   - Create new provider
   - Create Messaging API channel
   - Get Channel Access Token and Channel Secret

2. Get your LINE User ID:
   - Add official LINE account as friend
   - Send any message
   - Check webhook logs for user ID

3. Update secrets file:
```bash
sudo nano /home/pi/rpi-monitoring/config/secrets.json
```

```json
{
  "line": {
    "channel_access_token": "YOUR_TOKEN_HERE",
    "channel_secret": "YOUR_SECRET_HERE",
    "user_id": "YOUR_USER_ID_HERE"
  }
}
```

### 6. Start Services

Enable and start the monitoring service:
```bash
sudo systemctl enable rpi-monitoring
sudo systemctl start rpi-monitoring
```

Check status:
```bash
sudo systemctl status rpi-monitoring
```

View logs:
```bash
sudo journalctl -u rpi-monitoring -f
```

### 7. Test System

1. Walk in front of camera - should trigger motion detection
2. Check LINE app for notification
3. Reply "stop" to disable detection
4. Reply "resume" to enable detection

## Troubleshooting

### Camera Not Connecting
- Verify RTSP URL is correct
- Check camera is on same network
- Test RTSP URL with VLC media player

### No LINE Notifications
- Verify LINE credentials are correct
- Check internet connection
- View logs: `sudo journalctl -u rpi-monitoring -f`

### High CPU Usage
- Reduce camera resolution in config.yaml
- Lower FPS setting
- Disable auto-tracking if not needed

### Servo Not Moving
- Check PCA9685 I2C connection
- Verify servo power supply (separate 5V)
- Test with: `sudo i2cdetect -y 1`

## Maintenance

### Update System
The system automatically checks for updates every hour. To manually update:
```bash
sudo systemctl restart rpi-monitoring
```

### View Snapshots
```bash
ls -lh /home/pi/rpi-monitoring/snapshots/
```

### Clear Old Snapshots
```bash
find /home/pi/rpi-monitoring/snapshots/ -mtime +7 -delete
```

## Support

For issues or questions, contact: Abdul Raheem Ansari

