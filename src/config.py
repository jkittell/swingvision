import logging
import sys

# Configure console handler for errors only
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)  # Only show errors in console
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))  # Simpler format for console

# Create a logger object for this module
logger = logging.getLogger(__name__)