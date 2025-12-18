"""
Fall Detection Demo.

Demonstrates fall detection with webcam or video file.
Shows real-time visualization with person state and fall alerts.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Usage:
    python examples/fall_detection_demo.py                    # Use webcam
    python examples/fall_detection_demo.py --video test.mp4   # Use video file
"""

import cv2
import argparse
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detection import FallDetector, PersonState, EventLogger


def main():
    """Run fall detection demo."""
    parser = argparse.ArgumentParser(description="Fall Detection Demo")
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to video file (default: use webcam)"
    )
    parser.add_argument(
        "--aspect-ratio",
        type=float,
        default=1.5,
        help="Aspect ratio threshold (default: 1.5)"
    )
    parser.add_argument(
        "--velocity",
        type=float,
        default=0.3,
        help="Fall velocity threshold (default: 0.3)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Inactivity timeout in seconds (default: 10.0)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable video display (headless mode)"
    )
    parser.add_argument(
        "--save-events",
        action="store_true",
        help="Save fall events to disk"
    )
    
    args = parser.parse_args()
    
    # Initialize video capture
    if args.video:
        print(f"Opening video file: {args.video}")
        cap = cv2.VideoCapture(args.video)
    else:
        print("Opening webcam...")
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open video source")
        return
    
    # Initialize fall detector
    print(f"Initializing fall detector...")
    print(f"  Aspect ratio threshold: {args.aspect_ratio}")
    print(f"  Velocity threshold: {args.velocity}")
    print(f"  Inactivity timeout: {args.timeout}s")
    
    event_logger = None
    if args.save_events:
        event_logger = EventLogger()
        print(f"Event logging enabled: {event_logger.log_dir}")
    
    def fall_callback(frame, bbox, velocity):
        """Callback when fall detected."""
        if event_logger:
            event_logger.log_event("fall", frame, {
                "bbox": bbox,
                "velocity": velocity
            })
        print(f"\n!!! FALL DETECTED !!! Velocity: {velocity:.2f}\n")
    
    detector = FallDetector(
        aspect_ratio_threshold=args.aspect_ratio,
        fall_velocity_threshold=args.velocity,
        inactivity_timeout=args.timeout,
        fall_callback=fall_callback if args.save_events else None
    )
    
    # Statistics
    frame_count = 0
    fall_count = 0
    start_time = time.time()
    fps = 0
    
    print("Starting fall detection... Press 'q' to quit")
    print("Press 's' to show statistics")
    print("Press 'r' to reset detector")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if args.video:
                    # Loop video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("Error: Failed to read frame")
                    break
            
            frame_count += 1
            
            # Detect fall
            fall_detected, person_state, bbox = detector.detect(frame)
            
            if fall_detected:
                fall_count += 1
            
            # Calculate FPS
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
            
            # Display
            if not args.no_display:
                # Draw fall detection
                display_frame = detector.draw_detection(frame, bbox, person_state)
                
                # Draw statistics
                cv2.putText(
                    display_frame,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    display_frame,
                    f"Falls: {fall_count}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                # Show state
                state_text = f"State: {person_state.value.upper()}"
                state_color = (0, 255, 0)
                if person_state == PersonState.FALLEN:
                    state_color = (0, 0, 255)
                elif person_state == PersonState.LYING:
                    state_color = (0, 165, 255)

                cv2.putText(
                    display_frame,
                    state_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    state_color,
                    2
                )

                cv2.imshow("Fall Detection Demo", display_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                stats = detector.get_stats()
                print("\n--- Statistics ---")
                print(f"Total frames: {stats['total_frames']}")
                print(f"Fall events: {stats['fall_count']}")
                print(f"Current state: {stats['current_state']}")
                print(f"FPS: {fps:.1f}")
                if stats['fall_time']:
                    print(f"Last fall: {time.time() - stats['fall_time']:.1f}s ago")
                print("------------------\n")
            elif key == ord('r'):
                detector.reset()
                frame_count = 0
                fall_count = 0
                start_time = time.time()
                print("Detector reset")

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

        # Final statistics
        print("\n=== Final Statistics ===")
        print(f"Total frames processed: {frame_count}")
        print(f"Fall events detected: {fall_count}")
        print(f"Average FPS: {fps:.1f}")
        if event_logger:
            print(f"Events logged: {event_logger.get_event_count()}")
        print("========================\n")


if __name__ == "__main__":
    main()

