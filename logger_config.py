import logging
import os
from datetime import datetime
from pathlib import Path

class LoggerConfig:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        (self.log_dir / "info").mkdir(exist_ok=True)
        (self.log_dir / "warning").mkdir(exist_ok=True)
        (self.log_dir / "debug").mkdir(exist_ok=True)
        (self.log_dir / "error").mkdir(exist_ok=True)
        (self.log_dir / "intent").mkdir(exist_ok=True)
        
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup different loggers for different log levels"""
        
        # Info Logger
        self.info_logger = logging.getLogger('info')
        self.info_logger.setLevel(logging.INFO)
        info_handler = logging.FileHandler(
            self.log_dir / "info" / f"info_{datetime.now().strftime('%Y%m%d')}.log"
        )
        info_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        info_handler.setFormatter(info_formatter)
        self.info_logger.addHandler(info_handler)
        
        # Warning Logger
        self.warning_logger = logging.getLogger('warning')
        self.warning_logger.setLevel(logging.WARNING)
        warning_handler = logging.FileHandler(
            self.log_dir / "warning" / f"warning_{datetime.now().strftime('%Y%m%d')}.log"
        )
        warning_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        warning_handler.setFormatter(warning_formatter)
        self.warning_logger.addHandler(warning_handler)
        
        # Debug Logger
        self.debug_logger = logging.getLogger('debug')
        self.debug_logger.setLevel(logging.DEBUG)
        debug_handler = logging.FileHandler(
            self.log_dir / "debug" / f"debug_{datetime.now().strftime('%Y%m%d')}.log"
        )
        debug_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        self.debug_logger.addHandler(debug_handler)
        
        # Error Logger
        self.error_logger = logging.getLogger('error')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(
            self.log_dir / "error" / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Intent Logger
        self.intent_logger = logging.getLogger('intent')
        self.intent_logger.setLevel(logging.INFO)
        intent_handler = logging.FileHandler(
            self.log_dir / "intent" / f"intent_{datetime.now().strftime('%Y%m%d')}.log"
        )
        intent_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        intent_handler.setFormatter(intent_formatter)
        self.intent_logger.addHandler(intent_handler)
    
    def log_info(self, message, session_id=None, user_id=None):
        """Log info level messages"""
        log_msg = f"Session: {session_id or 'N/A'} | User: {user_id or 'N/A'} | {message}"
        self.info_logger.info(log_msg)
    
    def log_warning(self, message, session_id=None, user_id=None):
        """Log warning level messages"""
        log_msg = f"Session: {session_id or 'N/A'} | User: {user_id or 'N/A'} | {message}"
        self.warning_logger.warning(log_msg)
    
    def log_debug(self, message, session_id=None, user_id=None):
        """Log debug level messages"""
        log_msg = f"Session: {session_id or 'N/A'} | User: {user_id or 'N/A'} | {message}"
        self.debug_logger.debug(log_msg)
    
    def log_error(self, message, session_id=None, user_id=None, exception=None):
        """Log error level messages"""
        log_msg = f"Session: {session_id or 'N/A'} | User: {user_id or 'N/A'} | {message}"
        if exception:
            log_msg += f" | Exception: {str(exception)}"
        self.error_logger.error(log_msg)
    
    def log_intent(self, message, intent, confidence, session_id=None, user_id=None):
        """Log intent classification results"""
        log_msg = f"Session: {session_id or 'N/A'} | User: {user_id or 'N/A'} | Message: '{message}' | Intent: {intent} | Confidence: {confidence:.2f}"
        self.intent_logger.info(log_msg)

# Global logger instance
logger_config = LoggerConfig()
