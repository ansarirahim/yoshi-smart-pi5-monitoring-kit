"""
LINE Webhook Demo Script.

Demonstrates webhook server setup and command handling.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.line_api import WebhookServer  # noqa: E402
from src.detection import MotionDetector, FallDetector  # noqa: E402
from src.utils.logger import setup_logger  # noqa: E402


def main():
    """Run webhook demo."""
    # Load environment variables
    load_dotenv()

    # Setup logger
    logger = setup_logger("WebhookDemo")
    logger.info("Starting LINE Webhook Demo")

    # Get credentials from environment
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    channel_secret = os.getenv("LINE_CHANNEL_SECRET")

    if not channel_access_token or not channel_secret:
        logger.error("Missing LINE credentials in environment variables")
        logger.error("Please set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET")
        return

    # Initialize detectors (mock for demo)
    logger.info("Initializing detection system...")
    motion_detector = MotionDetector()
    fall_detector = FallDetector()

    # Command handler
    def handle_command(command: str):
        """Handle webhook commands."""
        logger.info(f"Processing command: {command}")

        if command == "stop":
            logger.info("Stopping detection...")
            motion_detector.pause()
            fall_detector.pause()
            logger.info("Detection stopped")

        elif command == "resume":
            logger.info("Resuming detection...")
            motion_detector.resume()
            fall_detector.resume()
            logger.info("Detection resumed")

        elif command == "status":
            motion_status = "paused" if motion_detector.is_paused() else "running"
            fall_status = "paused" if fall_detector.is_paused() else "running"
            logger.info(f"Status - Motion: {motion_status}, Fall: {fall_status}")

    # Initialize webhook server
    logger.info("Initializing webhook server...")
    webhook = WebhookServer(
        channel_access_token=channel_access_token,
        channel_secret=channel_secret,
        command_callback=handle_command,
        host="0.0.0.0",
        port=5000
    )

    # Start server
    logger.info("Starting webhook server on http://0.0.0.0:5000")
    webhook.start()

    logger.info("=" * 60)
    logger.info("Webhook server is running!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Setup Instructions:")
    logger.info("1. Go to LINE Developers Console")
    logger.info("2. Set webhook URL: http://your-domain.com:5000/webhook")
    logger.info("3. For local testing, use ngrok:")
    logger.info("   - Run: ngrok http 5000")
    logger.info("   - Copy ngrok URL and set as webhook URL")
    logger.info("")
    logger.info("Available Commands:")
    logger.info("- stop   : Stop detection")
    logger.info("- resume : Resume detection")
    logger.info("- status : Check system status")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        webhook.stop()
        logger.info("Webhook server stopped")


if __name__ == "__main__":
    main()
