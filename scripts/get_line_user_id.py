#!/usr/bin/env python3
"""
Get LINE User ID from incoming messages.

Run this script and have Yoshi send any message to the bot.
The script will print his User ID which we need for sending notifications.

Usage:
    python3 scripts/get_line_user_id.py

Then ask Yoshi to send any message to the bot (@514otjkn).
"""

import os
import sys
from flask import Flask, request, abort
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

print("=" * 60)
print("LINE User ID Capture Server")
print("=" * 60)
print(f"Channel Secret: {CHANNEL_SECRET[:10]}..." if CHANNEL_SECRET else "NOT SET")
print(f"Access Token: {CHANNEL_ACCESS_TOKEN[:20]}..." if CHANNEL_ACCESS_TOKEN else "NOT SET")
print("=" * 60)
print("\nWaiting for Yoshi to send a message to bot @514otjkn...")
print("The User ID will appear below:\n")

@app.route("/webhook", methods=['POST'])
def webhook():
    """Handle incoming LINE webhook events."""
    body = request.get_json()
    
    if body and 'events' in body:
        for event in body['events']:
            if 'source' in event:
                source = event['source']
                user_id = source.get('userId', 'N/A')
                
                print("\n" + "=" * 60)
                print("USER ID FOUND!")
                print("=" * 60)
                print(f"\nLINE_USER_ID={user_id}\n")
                print("=" * 60)
                print("\nCopy this User ID and add it to the .env file!")
                print("Then restart the monitoring service.\n")
                
                # Also print event details
                print(f"Event Type: {event.get('type', 'unknown')}")
                if event.get('type') == 'message':
                    message = event.get('message', {})
                    print(f"Message Type: {message.get('type', 'unknown')}")
                    if message.get('type') == 'text':
                        print(f"Message Text: {message.get('text', '')}")
    
    return 'OK', 200

@app.route("/", methods=['GET'])
def index():
    """Health check endpoint."""
    return "LINE User ID Capture Server is running. Send a message to the bot!", 200

if __name__ == '__main__':
    print("\nStarting server on port 5000...")
    print("Make sure port 5000 is accessible from the internet")
    print("(or use ngrok/localtunnel for testing)\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

