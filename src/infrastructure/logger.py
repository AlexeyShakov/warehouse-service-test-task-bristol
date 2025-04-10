import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = "warehouse_service.log"

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Full path to log file
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Rotating file handler (rotate when >5MB, keep 5 backups)
file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
file_handler.setFormatter(formatter)

# Main logger setup
LOGGER = logging.getLogger("warehouse_logger")
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(console_handler)
LOGGER.addHandler(file_handler)
