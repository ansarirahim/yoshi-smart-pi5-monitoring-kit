#!/usr/bin/env python3
"""
Test LINE API and try to get bot info.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

print("=" * 60)
print("LINE API Test")
print("=" * 60)

# Test 1: Get Bot Info
print("\n1. Getting Bot Info...")
headers = {
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get('https://api.line.me/v2/bot/info', headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    bot_info = response.json()
    print(f"Bot Name: {bot_info.get('displayName', 'N/A')}")
    print(f"Bot User ID: {bot_info.get('userId', 'N/A')}")
    print(f"Basic ID: {bot_info.get('basicId', 'N/A')}")
else:
    print(f"Error: {response.text}")

# Test 2: Get Followers (if available)
print("\n2. Getting Followers...")
response = requests.get('https://api.line.me/v2/bot/followers/ids', headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    user_ids = data.get('userIds', [])
    print(f"Found {len(user_ids)} followers")
    for uid in user_ids:
        print(f"  User ID: {uid}")
else:
    print(f"Error: {response.text}")

print("\n" + "=" * 60)

