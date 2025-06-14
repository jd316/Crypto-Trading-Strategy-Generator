# app/utils.py
import logging

def setup_logger():
    """
    Set up a logger for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)

def validate_input(user_input):
    """
    Validate user input to ensure it's not empty or invalid.
    :param user_input: User input as a string
    :return: True if valid, False otherwise
    """
    if not user_input or len(user_input.strip()) == 0:
        return False
    return True