# Yoshi's Smart Monitoring Kit - Quick Setup Guide

## 🔌 Plug and Play Setup

### Step 1: Power On
1. Connect all sensors as per GPIO wiring diagram
2. Connect power supply to Raspberry Pi
3. System will auto-start monitoring

### Step 2: Configure LINE Notifications (Optional)
Edit the environment file:
```bash
sudo nano /etc/environment
```

Add your LINE credentials:
```
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_USER_ID=your_user_id_here
LINE_CHANNEL_SECRET=your_secret_here
```

### Step 3: Start Monitoring
```bash
cd ~/monitoring
./start.sh
```

---

## 🔧 Manual Commands

| Command | Description |
|---------|-------------|
| `./start.sh` | Start monitoring |
| `./start.sh --test` | Test all sensors |
| `./start.sh --status` | Check system status |

---

## 📱 LINE Commands (via Chat)

| Command | Action |
|---------|--------|
| `status` | Get sensor status |
| `arm` | Enable alerts |
| `disarm` | Disable alerts |
| `stop` | Pause monitoring |
| `resume` | Resume monitoring |

---

## 🔌 GPIO Wiring

| Sensor | GPIO | Pin | VCC | GND |
|--------|------|-----|-----|-----|
| PIR Motion | GPIO17 | 11 | 3.3V | GND |
| Sound | GPIO22 | 15 | 3.3V | GND |
| Door | GPIO23 | 16 | - | GND |
| Vibration | GPIO27 | 13 | 3.3V | GND |
| Temperature | USB-RS485 | - | - | - |

---

## ⚙️ Auto-Start Service

Install as system service:
```bash
sudo cp yoshi-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable yoshi-monitor
sudo systemctl start yoshi-monitor
```

Check status:
```bash
sudo systemctl status yoshi-monitor
```

View logs:
```bash
journalctl -u yoshi-monitor -f
```

---

## 🔔 Alert Types

| Alert | Trigger |
|-------|---------|
| 🚨 Break-in | Vibration detected without door opening |
| 👤 Night Motion | Motion detected during night hours (22:00-06:00) |
| 🚪 Door Alert | Door opened at night |
| 🔊 Sound Alert | Loud sound detected |
| 🌡️ Temp Alert | Temperature outside 15-35°C range |

---

## 📁 Project Structure

```
monitoring/
├── start.sh           # Startup script
├── SETUP.md           # This file
├── src/
│   ├── sensors/       # Sensor drivers
│   ├── monitoring/    # Main monitoring system
│   ├── line_api/      # LINE integration
│   └── ota/           # OTA updates
├── tests/             # Test scripts
└── docs/              # Documentation
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Sensors not working | Run `./start.sh --test` |
| No LINE notifications | Check LINE credentials |
| Service won't start | Check `journalctl -u yoshi-monitor` |

---

**Enjoy your Smart Monitoring Kit! 🏠**

