import logging
import sys

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
GREEN = "\033[32m"

class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: RED
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"

def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    
    # Only add handler if the logger doesn't already have handlers
    if not logger.handlers:
        logger.setLevel(level)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Format
        formatter = ColoredFormatter('%(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        # Uncomment the following lines if you also want to log to a file
        # file_handler = logging.FileHandler('app.log')
        # file_handler.setLevel(level)
        # file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        # logger.addHandler(file_handler)

    return logger
