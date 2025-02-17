import logging
import os

def setup_logging():
    """Configure logging for the application"""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraping.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_to_file(response, file_name, dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    with open(f"{dir_name}/{file_name}", "a") as f:
        f.write(response)


def log_time(model, language, duration):
    with open("logger.txt", "a") as f:
        f.write(f"Model: {model}, Language: {language}, Duration: {duration}")