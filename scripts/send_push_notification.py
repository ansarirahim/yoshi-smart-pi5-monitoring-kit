#!/usr/bin/env python3
"""
Send PUSH notification directly to Yoshi's LINE.
This uses his personal User ID for direct messaging.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
USER_ID = os.getenv('LINE_USER_ID', '')

print("=" * 60)
print("Sending PUSH Notification to Yoshi")
print("=" * 60)
print(f"User ID: {USER_ID[:10]}...{USER_ID[-5:]}")
print()

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

# Push message to specific user
data = {
    "to": USER_ID,
    "messages": [
        {
            "type": "text",
            "text": "🎉 Direct Push Notification Test!\n\nHi Yoshi!\n\nThis message was sent DIRECTLY to your LINE using your User ID.\n\n✅ Push notification is working!\n\nYour Smart Monitoring Kit will now send alerts directly to YOU when:\n• Motion is detected\n• Door opens/closes\n• Vibration detected\n• Sound detected\n• Temperature changes\n\nThank you for your patience!\n\n- A.R. Ansari"
        }
    ]
}

response = requests.post(
    'https://api.line.me/v2/bot/message/push',
    headers=headers,
    json=data
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ PUSH notification sent successfully!")
    print("Yoshi should receive this message RIGHT NOW!")
else:
    print(f"Error: {response.text}")

print("=" * 60)

