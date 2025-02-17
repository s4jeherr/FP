import logging
import os
import csv
from datetime import datetime
from .departments.guedingen import GuedingenScraper
from .departments.pluwig import PluwigScraper
from .departments.oppenheim import OppenheimScraper
from database import Neo4jService

class ScrapingManager:
    """Manages the scraping process for all fire departments"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scrapers = [
            GuedingenScraper(),
            PluwigScraper(),
            OppenheimScraper(),
        ]
        # Create data directory if it doesn't exist
        self.data_dir = "/home/project/data/reports"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_to_txt(self, reports, scraper_name, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        for idx, report in enumerate(reports['ReportText'], start=1):
            file_name = f"{scraper_name}_{idx}.txt"
            file_path = os.path.join(directory, file_name)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(report)

    def run_all_scrapers(self):
        """Run all scrapers and store results in Neo4j and CSV"""
        for scraper in self.scrapers:
            try:
                self.logger.info(f"Starting scraper: {scraper.__class__.__name__}")
                reports = scraper.scrape()

                self.save_to_txt(reports, scraper.__class__.__name__, "reports")
                self.logger.info(f"Completed scraping for {scraper.__class__.__name__}")

            except Exception as e:
                self.logger.error(f"Error in scraper {scraper.__class__.__name__}: {str(e)}")
                continue