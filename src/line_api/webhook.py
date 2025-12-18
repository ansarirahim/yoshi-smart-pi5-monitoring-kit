#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE Webhook Server Module.

@file       webhook.py
@brief      Receives webhook events from LINE Platform.
@details    Processes commands from LINE with signature verification
            for secure remote control of the monitoring system.

@author     A.R. Ansari
@email      ansarirahim1@gmail.com
@phone      +91 9024304881
@linkedin   https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/

@project    Raspberry Pi Smart Monitoring Kit
@client     Yoshinori Ueda
@version    1.0.0
@date       2024-12-04
@copyright  (c) 2024 A.R. Ansari. All rights reserved.

@dependencies
    - line-bot-sdk >= 3.0.0
    - flask >= 2.0.0
"""

import threading
from typing import Optional, Callable
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from src.utils.logger import setup_logger


class WebhookServer:
    """
    LINE webhook server for receiving and processing commands.

    Handles incoming webhook events from LINE Platform with signature
    verification and command processing.

    Args:
        channel_access_token: LINE channel access token
        channel_secret: LINE channel secret for signature verification
        command_callback: Callback function(command: str) for processing commands
        host: Server host address
        port: Server port number

    Example:
        def handle_command(command):
            if command == "stop":
                # Stop detection
                pass

        server = WebhookServer(
            channel_access_token="YOUR_TOKEN",
            channel_secret="YOUR_SECRET",
            command_callback=handle_command
        )

        server.start()
    """

    def __init__(
        self,
        channel_access_token: str,
        channel_secret: str,
        command_callback: Optional[Callable[[str], None]] = None,
        host: str = "0.0.0.0",
        port: int = 5000
    ):
        """Initialize webhook server."""
        if not channel_access_token:
            raise ValueError("channel_access_token is required")
        if not channel_secret:
            raise ValueError("channel_secret is required")

        self.channel_access_token = channel_access_token
        self.channel_secret = channel_secret
        self.command_callback = command_callback
        self.host = host
        self.port = port

        self.logger = setup_logger("WebhookServer")

        # Initialize Flask app
        self.app = Flask(__name__)

        # Initialize LINE webhook handler
        self.handler = WebhookHandler(channel_secret)

        # Initialize LINE messaging API
        configuration = Configuration(access_token=channel_access_token)
        self.api_client = ApiClient(configuration)
        self.messaging_api = MessagingApi(self.api_client)

        # Server state
        self.running = False
        self.server_thread = None

        # Setup routes and handlers
        self._setup_routes()
        self._setup_handlers()

        self.logger.info("Webhook server initialized")

    def _setup_routes(self):
        """Setup Flask routes."""
        @self.app.route("/webhook", methods=["POST"])
        def webhook():
            """Handle webhook POST requests."""
            # Get signature from header
            signature = request.headers.get("X-Line-Signature")
            if not signature:
                self.logger.warning("Missing X-Line-Signature header")
                abort(400)

            # Get request body
            body = request.get_data(as_text=True)
            self.logger.debug(f"Webhook received: {body}")

            # Verify signature and handle events
            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                self.logger.error("Invalid signature")
                abort(400)

            return "OK"

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return {"status": "ok", "running": self.running}

    def _setup_handlers(self):
        """Setup LINE event handlers."""
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_message(event):
            """Handle text message events."""
            text = event.message.text.strip().lower()
            self.logger.info(f"Received message: {text}")

            # Process command
            response = self._process_command(text)

            # Send reply
            self.messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)]
                )
            )

    def _process_command(self, command: str) -> str:
        """
        Process incoming command.

        Args:
            command: Command text (lowercase)

        Returns:
            Response message
        """
        if command == "stop":
            if self.command_callback:
                self.command_callback("stop")
            return "Detection stopped. Send 'resume' to restart."

        elif command == "resume":
            if self.command_callback:
                self.command_callback("resume")
            return "Detection resumed."

        elif command == "status":
            if self.command_callback:
                self.command_callback("status")
            return "System is running."

        else:
            return (
                "Unknown command. Available commands:\n"
                "- stop: Stop detection\n"
                "- resume: Resume detection\n"
                "- status: Check system status"
            )

    def start(self):
        """Start webhook server in background thread."""
        if self.running:
            self.logger.warning("Server already running")
            return

        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        self.logger.info(f"Webhook server started on {self.host}:{self.port}")

    def _run_server(self):
        """Run Flask server."""
        self.app.run(host=self.host, port=self.port, debug=False)

    def stop(self):
        """Stop webhook server."""
        self.running = False
        self.logger.info("Webhook server stopped")

    def is_running(self) -> bool:
        """
        Check if server is running.

        Returns:
            True if running, False otherwise
        """
        return self.running
