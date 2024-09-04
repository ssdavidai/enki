# utils.py

import os
import logging
from datetime import datetime
import threading
import time

# Logging setup
def setup_logging(log_dir="simulation_logs"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# Utility for generating unique IDs
_id_counter = 0
_id_lock = threading.Lock()

def generate_id():
    global _id_counter
    with _id_lock:
        _id_counter += 1
        return f"{int(time.time() * 1000)}_{_id_counter}"

# Error handling utility
def handle_index_error(world, e):
    logging.error(f"IndexError: {e}")
    world.handle_index_error()

# Logging decorator for method tracing
def logging_decorator(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Entering {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Exiting {func.__name__}")
        return result
    return wrapper
