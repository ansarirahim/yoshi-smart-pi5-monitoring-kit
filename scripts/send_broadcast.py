#!/usr/bin/env python3
"""
Send broadcast message to all LINE bot followers.
This sends to ALL followers of the bot.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

print("=" * 60)
print("Sending Broadcast Message to ALL Followers")
print("=" * 60)

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

# Broadcast message
data = {
    "messages": [
        {
            "type": "text",
            "text": "🎉 Smart Monitoring System Connected!\n\nThis is a test message from your Raspberry Pi Smart Monitoring Kit.\n\nThe system is now configured and ready.\n\n- Motion Detection: ✅\n- Sound Detection: ✅\n- Door Sensor: ✅\n- Vibration Sensor: ✅\n- Temperature Monitor: ✅\n\nYou will receive alerts when sensors trigger.\n\nCommands:\n• status - Get sensor status\n• arm - Enable alerts\n• disarm - Disable alerts"
        }
    ]
}

response = requests.post(
    'https://api.line.me/v2/bot/message/broadcast',
    headers=headers,
    json=data
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Broadcast sent successfully!")
    print("Yoshi should receive this message now!")
else:
    print(f"Error: {response.text}")

print("=" * 60)

