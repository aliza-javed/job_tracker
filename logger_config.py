"""
logger_config.py
----------------
Logging module - Python mein debugging aur tracking ke liye use hota hai.
Har action log hoga file mein.
"""

import logging
from datetime import datetime

def setup_logger():
    """
    Logger setup karta hai.
    - File mein save hoga
    - Console mein bhi dikhega
    - Format: timestamp - level - message
    """
    
    # Logger create karo
    logger = logging.getLogger("JobTracker")
    logger.setLevel(logging.DEBUG)  # Sabse low level - sab kuch log hoga
    
    # Agar handlers already hain toh dobara add mat karo
    if logger.handlers:
        return logger
    
    # File handler - file mein log save karega
    file_handler = logging.FileHandler("job_tracker.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler - terminal mein dikhega
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format set karo
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    # Handlers add karo
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Test
if __name__ == "__main__":
    log = setup_logger()
    log.info("Logger test successful!")
    log.debug("This is a debug message")
    log.warning("This is a warning")