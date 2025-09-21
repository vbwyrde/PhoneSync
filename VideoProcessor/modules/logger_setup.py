"""
Logging Setup for PhoneSync + VideoProcessor
Configures comprehensive logging with rotation and retention
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up comprehensive logging system
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger instance
    """
    log_config = config['logging']
    
    # Create logger
    logger = logging.getLogger('phone_sync')
    logger.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if logging enabled)
    if log_config.get('enabled', True):
        log_path = Path(log_config['log_path'])
        
        # Create log directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        max_bytes = log_config.get('max_log_size_mb', 10) * 1024 * 1024
        backup_count = log_config.get('keep_log_days', 14)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(getattr(logging, log_config.get('log_level', 'INFO')))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Set verbose logging if requested
    if config['options'].get('verbose_logging', False):
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    
    return logger

def log_system_info(logger: logging.Logger, config: Dict[str, Any]):
    """Log system and configuration information"""
    import sys
    import platform
    from datetime import datetime
    
    logger.info("=== System Information ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    logger.info("=== Configuration Summary ===")
    logger.info(f"Source folders: {len(config['source_folders'])}")
    logger.info(f"Deduplication enabled: {config['options']['enable_deduplication']}")
    logger.info(f"Video analysis enabled: {not config['development']['skip_video_analysis']}")
    logger.info(f"Dry run mode: {config['options']['dry_run']}")

class ProgressLogger:
    """Helper class for progress reporting"""
    
    def __init__(self, logger: logging.Logger, total_items: int, report_interval: int = 100):
        """
        Initialize progress logger
        
        Args:
            logger: Logger instance
            total_items: Total number of items to process
            report_interval: Report progress every N items
        """
        self.logger = logger
        self.total_items = total_items
        self.report_interval = report_interval
        self.processed_items = 0
    
    def update(self, increment: int = 1):
        """Update progress counter and log if needed"""
        self.processed_items += increment
        
        if self.processed_items % self.report_interval == 0 or self.processed_items == self.total_items:
            percentage = (self.processed_items / self.total_items) * 100
            self.logger.info(f"Progress: {percentage:.1f}% ({self.processed_items}/{self.total_items})")
    
    def log_completion(self):
        """Log completion message"""
        self.logger.info(f"Processing complete: {self.processed_items}/{self.total_items} items")
