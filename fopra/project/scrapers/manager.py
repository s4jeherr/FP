import logging
import os
import csv
from datetime import datetime
from departments import (
    GuedingenScraper,
    PluwigScraper,
    OppenheimScraper,
    RuebenachScraper
)
from database import Neo4jService

class ScrapingManager:
    """Manages the scraping process for all fire departments"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.neo4j = Neo4jService()
        self.scrapers = [
            GuedingenScraper(),
            PluwigScraper(),
            OppenheimScraper(),
            RuebenachScraper()
        ]
        # Create data directory if it doesn't exist
        self.data_dir = "/home/project/data/reports"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_to_csv(self, reports, scraper_name):
        """Save reports to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.data_dir}/{scraper_name}_{timestamp}.csv"

        fieldnames = ['einsatzart', 'ort', 'datum', 'dauer', 'beteiligte', 'verlauf']

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for report in reports:
                    row = report.to_dict()
                    # Convert list to string for CSV storage
                    if isinstance(row['beteiligte'], list):
                        row['beteiligte'] = ','.join(row['beteiligte'])
                    writer.writerow(row)
            self.logger.info(f"Saved {len(reports)} reports to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save CSV file: {str(e)}")

    def run_all_scrapers(self):
        """Run all scrapers and store results in Neo4j and CSV"""
        for scraper in self.scrapers:
            try:
                self.logger.info(f"Starting scraper: {scraper.__class__.__name__}")
                reports = scraper.scrape()

                # Save raw data to CSV first
                self.save_to_csv(reports, scraper.__class__.__name__)

                # Try LLM analysis and Neo4j storage, but continue if they fail
                for report in reports:
                    try:
                        # Process report with LLM service
                        processed_report = scraper.llm_service.analyze_report(
                            report.verlauf,
                            report.datum
                        )

                        # Store in Neo4j
                        self.neo4j.store_report(processed_report)
                    except Exception as e:
                        self.logger.warning(f"Failed to process report with LLM/Neo4j: {str(e)}")
                        continue

                self.logger.info(f"Completed scraping for {scraper.__class__.__name__}")

            except Exception as e:
                self.logger.error(f"Error in scraper {scraper.__class__.__name__}: {str(e)}")
                continue