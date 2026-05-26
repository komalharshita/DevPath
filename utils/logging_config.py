import json
import logging
import time
from datetime import datetime, timezone
from flask import request, g

class JsonFormatter(logging.Formatter):
    """Custom standard logging Formatter that outputs logs in JSON format."""
    def format(self, record):
        # Base log fields
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Standard attributes of LogRecord to exclude from extra payload
        standard_fields = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        
        # Merge extra attributes if passed in the `extra` dictionary
        for key, value in record.__dict__.items():
            if key not in standard_fields:
                log_record[key] = value
                
        # If exc_info is present, format and add it as error/exception details
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging(app):
    """Set up application-wide JSON logging."""
    formatter = JsonFormatter()
    
    # Configure StreamHandler for logging to stdout/stderr
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    # Remove existing handlers to prevent duplicate formatting or logging
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Configure Flask app logger
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    
    # Silence default Werkzeug HTTP request logger to avoid plain text duplicates
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
