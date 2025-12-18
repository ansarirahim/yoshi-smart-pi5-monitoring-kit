"""
Motion Detection Demo.

Demonstrates motion detection with webcam or video file.
Shows real-time visualization with bounding boxes and statistics.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit

Usage:
    python examples/motion_detection_demo.py                    # Use webcam
    python examples/motion_detection_demo.py --video test.mp4   # Use video file
"""

import cv2
import argparse
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detection import MotionDetector, EventLogger


def main():
    """Run motion detection demo."""
    parser = argparse.ArgumentParser(description="Motion Detection Demo")
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to video file (default: use webcam)"
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=500,
        help="Minimum motion area in pixels (default: 500)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable video display (headless mode)"
    )
    parser.add_argument(
        "--save-events",
        action="store_true",
        help="Save motion events to disk"
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
    
    # Initialize motion detector
    print(f"Initializing motion detector (min_area={args.min_area})...")
    
    event_logger = None
    if args.save_events:
        event_logger = EventLogger()
        print(f"Event logging enabled: {event_logger.log_dir}")
    
    def motion_callback(frame, boxes):
        """Callback when motion detected."""
        if event_logger:
            event_logger.log_event("motion", frame, {"boxes": len(boxes)})
    
    detector = MotionDetector(
        min_area=args.min_area,
        motion_callback=motion_callback if args.save_events else None
    )
    
    # Statistics
    frame_count = 0
    motion_count = 0
    start_time = time.time()
    fps = 0
    
    print("Starting motion detection... Press 'q' to quit")
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
            
            # Detect motion
            motion_detected, bounding_boxes = detector.detect(frame)
            
            if motion_detected:
                motion_count += 1
            
            # Calculate FPS
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
            
            # Display
            if not args.no_display:
                # Draw motion boxes
                if motion_detected:
                    display_frame = detector.draw_motion(frame, bounding_boxes)
                else:
                    display_frame = frame.copy()
                
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
                    f"Motion: {motion_count}/{frame_count}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                if motion_detected:
                    cv2.putText(
                        display_frame,
                        f"MOTION DETECTED ({len(bounding_boxes)} objects)",
                        (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                
                cv2.imshow("Motion Detection Demo", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                stats = detector.get_stats()
                print("\n--- Statistics ---")
                print(f"Total frames: {stats['total_frames']}")
                print(f"Motion events: {stats['motion_count']}")
                print(f"FPS: {fps:.1f}")
                if stats['last_motion_time']:
                    print(f"Last motion: {time.time() - stats['last_motion_time']:.1f}s ago")
                print("------------------\n")
            elif key == ord('r'):
                detector.reset()
                frame_count = 0
                motion_count = 0
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
        print(f"Motion events detected: {motion_count}")
        print(f"Average FPS: {fps:.1f}")
        if event_logger:
            print(f"Events logged: {event_logger.get_event_count()}")
        print("========================\n")


if __name__ == "__main__":
    main()

