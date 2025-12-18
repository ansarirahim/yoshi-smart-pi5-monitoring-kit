#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging utility for Raspberry Pi Smart Monitoring Kit.

@file       logger.py
@brief      Centralized logging with file rotation and colored output.
@details    Provides configurable logging with rotating file handlers
            and colored console output for easy debugging.

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
    - colorlog >= 6.0.0
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorlog


def setup_logger(
    name: str,
    log_file: str = "logs/monitoring.log",
    level: str = "INFO",
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler with colors
    if console_output:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

