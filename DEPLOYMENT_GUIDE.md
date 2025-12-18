# Deployment Guide to Raspberry Pi 5

**Target RPI5:** 192.168.1.39  
**Username:** yoshi  
**Password:** ansari  
**Project Directory:** /home/yoshi/raspberry-pi-smart-monitoring

---

## Method 1: Using Git Clone (Recommended - Easiest)

### Step 1: SSH into RPI5

```bash
ssh yoshi@192.168.1.39
# Password: ansari
```

### Step 2: Clone Repository

```bash
cd /home/yoshi
git clone https://github.com/ansarirahim/raspberry-pi-smart-monitoring.git
cd raspberry-pi-smart-monitoring
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python dependencies
pip3 install -r requirements.txt

# Install system dependencies
sudo apt install -y python3-opencv python3-pygame
```

### Step 4: Configure Application

```bash
# Copy secrets template
cp config/secrets.example.json config/secrets.json

# Edit secrets (add LINE credentials)
nano config/secrets.json

# Edit config (add camera RTSP URL)
nano config/config.yaml
```

### Step 5: Create Audio File for Voice Alerts

```bash
# Create assets directory
mkdir -p assets

# Option 1: Use text-to-speech to generate audio
python3 << EOF
from gtts import gTTS
tts = gTTS("Are you OK?", lang='en')
tts.save("assets/are_you_ok.wav")
EOF

# Option 2: Download pre-recorded audio
# (You can upload your own audio file)
```

### Step 6: Run Tests

```bash
pytest tests/ -v
```

### Step 7: Test Application

```bash
python3 main.py
```

---

## Method 2: Using WinSCP (Windows GUI)

### Step 1: Download WinSCP

Download from: https://winscp.net/

### Step 2: Connect to RPI5

- **Protocol:** SFTP
- **Host:** 192.168.1.39
- **Port:** 22
- **Username:** yoshi
- **Password:** ansari

### Step 3: Transfer Files

1. Navigate to local directory:
   ```
   C:\Users\Abdul\Documents\augment-projects\Raspberry Pi Smart Monitoring Kit
   ```

2. Navigate to remote directory:
   ```
   /home/yoshi/
   ```

3. Create folder: `raspberry-pi-smart-monitoring`

4. Transfer these folders/files:
   - `src/`
   - `config/`
   - `docs/`
   - `examples/`
   - `scripts/`
   - `tests/`
   - `systemd/`
   - `assets/`
   - `main.py`
   - `requirements.txt`
   - `setup.py`
   - `pytest.ini`
   - `VERSION`
   - `README.md`

### Step 4: SSH and Configure

Follow Steps 3-7 from Method 1 above.

---

## Method 3: Using PowerShell Script (Requires PuTTY)

### Step 1: Install PuTTY

Download from: https://www.putty.org/

### Step 2: Run Deployment Script

```powershell
cd "C:\Users\Abdul\Documents\augment-projects\Raspberry Pi Smart Monitoring Kit"
.\scripts\deploy_to_rpi.ps1
```

### Step 3: Configure on RPI5

Follow Steps 4-7 from Method 1 above.

---

## Post-Deployment Configuration

### 1. Configure LINE API Credentials

Edit `config/secrets.json`:

```json
{
  "line": {
    "channel_access_token": "YOUR_LINE_CHANNEL_ACCESS_TOKEN",
    "channel_secret": "YOUR_LINE_CHANNEL_SECRET",
    "user_id": "YOUR_LINE_USER_ID"
  }
}
```

### 2. Configure Camera RTSP URL

Edit `config/config.yaml`:

```yaml
camera:
  rtsp_url: "rtsp://admin:password@192.168.1.200:554/stream"
  username: "admin"
  password: "your_camera_password"
```

### 3. Setup Systemd Service (Auto-start on Boot)

```bash
cd /home/yoshi/raspberry-pi-smart-monitoring

# Make install script executable
chmod +x scripts/install.sh

# Run installation
./scripts/install.sh

# Enable service
sudo systemctl enable rpi-monitoring
sudo systemctl start rpi-monitoring

# Check status
sudo systemctl status rpi-monitoring
```

---

## Verification Checklist

- [ ] Code transferred to RPI5
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] LINE credentials configured in `config/secrets.json`
- [ ] Camera RTSP URL configured in `config/config.yaml`
- [ ] Audio file created in `assets/are_you_ok.wav`
- [ ] Tests passing (`pytest tests/`)
- [ ] Application runs (`python3 main.py`)
- [ ] Systemd service enabled (optional)

---

## Troubleshooting

### Cannot SSH to RPI5

```bash
# Check if RPI5 is reachable
ping 192.168.1.39

# Check if SSH service is running on RPI5
# (Connect monitor/keyboard to RPI5)
sudo systemctl status ssh
sudo systemctl start ssh
```

### Missing Dependencies

```bash
# Install missing packages
sudo apt install -y python3-pip python3-opencv python3-pygame
pip3 install -r requirements.txt
```

### Permission Denied

```bash
# Fix permissions
chmod +x scripts/*.sh
chmod 644 config/config.yaml
chmod 600 config/secrets.json
```

---

## Quick Start Commands

```bash
# SSH into RPI5
ssh yoshi@192.168.1.39

# Clone and setup
git clone https://github.com/ansarirahim/raspberry-pi-smart-monitoring.git
cd raspberry-pi-smart-monitoring
pip3 install -r requirements.txt
cp config/secrets.example.json config/secrets.json
nano config/secrets.json  # Add LINE credentials
nano config/config.yaml   # Add camera RTSP URL

# Run application
python3 main.py
```

---

**Author:** A.R. Ansari  
**Email:** ansarirahim1@gmail.com

