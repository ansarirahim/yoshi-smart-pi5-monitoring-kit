#!/usr/bin/env python3
"""
Webhook server with file logging to capture User ID.
"""

import os
import json
from datetime import datetime
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
LOG_FILE = "/tmp/line_webhook.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

log("=" * 60)
log("LINE Webhook Server Started")
log("=" * 60)

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.get_json()
    log(f"Received webhook: {json.dumps(body, indent=2)}")
    
    if body and 'events' in body:
        for event in body['events']:
            if 'source' in event:
                user_id = event['source'].get('userId', 'N/A')
                log("=" * 60)
                log("!!! USER ID FOUND !!!")
                log(f"LINE_USER_ID={user_id}")
                log("=" * 60)
                
                # Save to a dedicated file
                with open("/tmp/yoshi_user_id.txt", "w") as f:
                    f.write(user_id)
    
    return 'OK', 200

@app.route("/", methods=['GET'])
def index():
    return "Webhook server running!", 200

if __name__ == '__main__':
    log("Starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)

