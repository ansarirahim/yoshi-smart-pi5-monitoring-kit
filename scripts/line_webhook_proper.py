#!/usr/bin/env python3
"""
Proper LINE Webhook Server with signature verification.
Captures User ID from incoming messages.
"""

import os
import json
import hashlib
import hmac
import base64
from datetime import datetime
from flask import Flask, request, abort
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
LOG_FILE = "/tmp/line_webhook.log"
USER_ID_FILE = "/tmp/yoshi_user_id.txt"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify LINE webhook signature."""
    if not CHANNEL_SECRET:
        log("WARNING: No channel secret, skipping verification")
        return True
    
    hash = hmac.new(
        CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash).decode('utf-8')
    
    return hmac.compare_digest(signature, expected_signature)

log("=" * 60)
log("LINE Webhook Server (with signature verification)")
log(f"Channel Secret: {CHANNEL_SECRET[:10]}..." if CHANNEL_SECRET else "NOT SET")
log("=" * 60)

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    """Handle incoming LINE webhook events."""
    # Handle GET request (for browser testing / LINE verification)
    if request.method == 'GET':
        return "Webhook endpoint ready! Waiting for LINE messages...", 200
    # Get signature from header
    signature = request.headers.get('X-Line-Signature', '')
    
    # Get raw body
    body = request.get_data()
    
    log(f"Received webhook - Signature: {signature[:20]}..." if signature else "No signature")
    log(f"Body: {body.decode('utf-8')[:200]}")
    
    # Verify signature
    if signature and not verify_signature(body, signature):
        log("ERROR: Invalid signature!")
        abort(400)
    
    # Parse JSON
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        log("ERROR: Invalid JSON")
        abort(400)
    
    # Extract user IDs from events
    if 'events' in data:
        for event in data['events']:
            if 'source' in event:
                user_id = event['source'].get('userId', '')
                if user_id:
                    log("=" * 60)
                    log("🎉 USER ID CAPTURED!")
                    log(f"LINE_USER_ID={user_id}")
                    log("=" * 60)
                    
                    # Save to file
                    with open(USER_ID_FILE, "w") as f:
                        f.write(user_id)
                    
                    # Also log event details
                    event_type = event.get('type', 'unknown')
                    log(f"Event Type: {event_type}")
                    if event_type == 'message':
                        msg = event.get('message', {})
                        log(f"Message: {msg.get('text', msg.get('type', 'N/A'))}")
    
    return 'OK', 200

@app.route("/", methods=['GET'])
def index():
    """Health check."""
    return "LINE Webhook Server Running! Send message to bot.", 200

if __name__ == '__main__':
    log("Starting server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

