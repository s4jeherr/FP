from scrapers.manager import ScrapingManager
from utils.utils import *
from dotenv import load_dotenv
import logging
import os

def main():
    # Load environment variables
    load_dotenv()

    logger = setup_logging()
    logger.info("Starting Fire Department Report Scraper")

    try:
        # Initialize and run scraping manager
        manager = ScrapingManager()
        manager.run_all_scrapers()

        logger.info("Scraping completed successfully")
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise

if __name__ == "__main__":
    main()