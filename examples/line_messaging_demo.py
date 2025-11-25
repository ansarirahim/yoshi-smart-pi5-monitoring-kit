"""
LINE Messaging Demo.

Demonstrates sending LINE notifications with optional snapshots.
Tests message formatting and error handling.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Usage:
    python examples/line_messaging_demo.py
    python examples/line_messaging_demo.py --with-snapshot
    python examples/line_messaging_demo.py --test-mode
"""

import argparse
import time
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2  # noqa: E402
from src.line_api import LINEMessenger  # noqa: E402


def main():
    """Run LINE messaging demo."""
    parser = argparse.ArgumentParser(description="LINE Messaging Demo")
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="LINE channel access token (or set LINE_CHANNEL_ACCESS_TOKEN env var)"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default=None,
        help="LINE user ID (or set LINE_USER_ID env var)"
    )
    parser.add_argument(
        "--with-snapshot",
        action="store_true",
        help="Include image snapshot in alert"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode (no actual messages sent)"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality for snapshots (default: 85)"
    )

    args = parser.parse_args()

    # Get credentials
    token = args.token or os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = args.user_id or os.getenv("LINE_USER_ID")

    if not token or not user_id:
        print("Error: LINE credentials not provided")
        print("Set environment variables:")
        print("  export LINE_CHANNEL_ACCESS_TOKEN='your_token'")
        print("  export LINE_USER_ID='your_user_id'")
        print("\nOr use command line arguments:")
        print("  --token YOUR_TOKEN --user-id YOUR_USER_ID")
        return

    print("LINE Messaging Demo")
    print("=" * 50)
    print(f"User ID: {user_id[:10]}...")
    print(f"Snapshot: {'Enabled' if args.with_snapshot else 'Disabled'}")
    print(f"Quality: {args.quality}")
    print(f"Test Mode: {'Yes' if args.test_mode else 'No'}")
    print("=" * 50)

    if args.test_mode:
        print("\nTest mode enabled - no messages will be sent")
        print("Simulating message sending...")
        time.sleep(1)
        print("Test complete!")
        return

    # Initialize messenger
    print("\nInitializing LINE messenger...")
    messenger = LINEMessenger(
        channel_access_token=token,
        user_id=user_id,
        send_snapshots=args.with_snapshot,
        snapshot_quality=args.quality
    )

    # Test 1: Simple text alert
    print("\nTest 1: Sending simple motion alert...")
    success = messenger.send_alert("motion")
    if success:
        print("✓ Motion alert sent successfully")
    else:
        print("✗ Failed to send motion alert")

    time.sleep(2)

    # Test 2: Alert with metadata
    print("\nTest 2: Sending fall alert with metadata...")
    success = messenger.send_alert("fall", metadata={
        "velocity": 0.75,
        "confidence": 0.92
    })
    if success:
        print("✓ Fall alert sent successfully")
    else:
        print("✗ Failed to send fall alert")

    time.sleep(2)

    # Test 3: Alert with snapshot (if enabled)
    if args.with_snapshot:
        print("\nTest 3: Sending alert with snapshot...")
        print("Opening webcam...")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("✗ Failed to open webcam")
            print("Creating test image instead...")
            frame = create_test_image()
        else:
            ret, frame = cap.read()
            cap.release()

            if not ret:
                print("✗ Failed to capture frame")
                print("Creating test image instead...")
                frame = create_test_image()
            else:
                print("✓ Frame captured from webcam")

        success = messenger.send_alert("motion", frame=frame, metadata={
            "area": 1500,
            "confidence": 0.88
        })

        if success:
            print("✓ Alert with snapshot sent successfully")
        else:
            print("✗ Failed to send alert with snapshot")

    # Test 4: Plain text message
    print("\nTest 4: Sending plain text message...")
    success = messenger.send_text("Demo completed successfully!")
    if success:
        print("✓ Text message sent successfully")
    else:
        print("✗ Failed to send text message")

    # Show statistics
    print("\n" + "=" * 50)
    print("Statistics:")
    stats = messenger.get_stats()
    print(f"  Messages sent: {stats['message_count']}")
    print(f"  Errors: {stats['error_count']}")
    if stats['last_message_time']:
        print(f"  Last message: {time.time() - stats['last_message_time']:.1f}s ago")
    print("=" * 50)

    print("\nDemo complete!")


def create_test_image():
    """Create a test image with text."""
    import numpy as np

    # Create blank image
    img = np.zeros((480, 640, 3), dtype=np.uint8)

    # Add text
    cv2.putText(
        img,
        "TEST IMAGE",
        (200, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255, 255, 255),
        3
    )

    return img


if __name__ == "__main__":
    main()
