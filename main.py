#!/usr/bin/env python3
"""
Raspberry Pi Smart Monitoring Kit - Main Application Entry Point.

This is the main orchestrator for the smart monitoring system, coordinating
all components including stream handling, detection, notifications, and control.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
WhatsApp: +919024304883
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Client: Yoshinori Ueda
Project: Raspberry Pi Smart Monitoring Kit
"""

import sys
import signal
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.logger import setup_logger
from utils.config_loader import ConfigLoader


class MonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize monitoring system"""
        self.logger = setup_logger("MonitoringSystem")
        self.config = ConfigLoader(config_path)
        self.running = False
        
        # Components (will be initialized in setup)
        self.rtsp_handler = None
        self.motion_detector = None
        self.fall_detector = None
        self.line_messenger = None
        self.webhook_server = None
        self.ota_updater = None
        self.voice_player = None
        self.pan_tilt_controller = None
        self.auto_tracker = None
        
        self.logger.info("Monitoring system initialized")
    
    def setup(self):
        """Setup all components"""
        self.logger.info("Setting up monitoring system...")
        
        try:
            # Import components
            from rtsp import RTSPStreamHandler
            from detection import MotionDetector, FallDetector
            from line_api import LINEMessenger, WebhookServer
            from ota import OTAUpdater
            from voice import VoiceAlertPlayer
            from pan_tilt import PanTiltController, AutoTracker
            
            # Initialize RTSP handler
            self.logger.info("Initializing RTSP stream handler...")
            self.rtsp_handler = RTSPStreamHandler(self.config.get("camera"))
            
            # Initialize detectors
            if self.config.get("motion_detection.enabled"):
                self.logger.info("Initializing motion detector...")
                self.motion_detector = MotionDetector(self.config.get("motion_detection"))
            
            if self.config.get("fall_detection.enabled"):
                self.logger.info("Initializing fall detector...")
                self.fall_detector = FallDetector(self.config.get("fall_detection"))
            
            # Initialize LINE messenger
            self.logger.info("Initializing LINE messenger...")
            self.line_messenger = LINEMessenger(self.config.get("line"))
            
            # Initialize webhook server
            if self.config.get("webhook.enabled"):
                self.logger.info("Initializing webhook server...")
                self.webhook_server = WebhookServer(
                    self.config.get("webhook"),
                    self.on_webhook_command
                )
            
            # Initialize OTA updater
            if self.config.get("ota.enabled"):
                self.logger.info("Initializing OTA updater...")
                self.ota_updater = OTAUpdater(self.config.get("ota"))
            
            # Initialize voice player
            if self.config.get("voice.enabled"):
                self.logger.info("Initializing voice alert player...")
                self.voice_player = VoiceAlertPlayer(self.config.get("voice"))
            
            # Initialize pan-tilt controller
            if self.config.get("pan_tilt.enabled"):
                self.logger.info("Initializing pan-tilt controller...")
                self.pan_tilt_controller = PanTiltController(self.config.get("pan_tilt"))
                
                if self.config.get("auto_tracking.enabled"):
                    self.logger.info("Initializing auto tracker...")
                    self.auto_tracker = AutoTracker(
                        self.config.get("auto_tracking"),
                        self.pan_tilt_controller
                    )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup components: {e}", exc_info=True)
            raise
    
    def on_webhook_command(self, command: str):
        """Handle webhook commands from LINE"""
        self.logger.info(f"Received webhook command: {command}")
        
        if command.lower() == "stop":
            self.pause_detection()
        elif command.lower() == "resume":
            self.resume_detection()
        else:
            self.logger.warning(f"Unknown command: {command}")
    
    def pause_detection(self):
        """Pause motion and fall detection"""
        self.logger.info("Pausing detection...")
        if self.motion_detector:
            self.motion_detector.pause()
        if self.fall_detector:
            self.fall_detector.pause()
    
    def resume_detection(self):
        """Resume motion and fall detection"""
        self.logger.info("Resuming detection...")
        if self.motion_detector:
            self.motion_detector.resume()
        if self.fall_detector:
            self.fall_detector.resume()
    
    def run(self):
        """Main run loop"""
        self.logger.info("Starting monitoring system...")
        self.running = True
        
        try:
            # Start webhook server in background
            if self.webhook_server:
                self.webhook_server.start()
            
            # Main processing loop
            while self.running:
                # Get frame from RTSP stream
                frame = self.rtsp_handler.get_frame()
                
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Process frame through detectors
                # (Actual implementation will be in milestone branches)
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down monitoring system...")
        self.running = False
        
        # Cleanup components
        # (Implementation in milestone branches)
        
        self.logger.info("Shutdown complete")


def signal_handler(signum, frame):
    """Handle system signals"""
    print("\nReceived signal to terminate. Shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run monitoring system
    system = MonitoringSystem()
    system.setup()
    system.run()


if __name__ == "__main__":
    main()

