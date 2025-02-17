from datetime import datetime
from typing import List
from .basescraper import BaseScraper

class RuebenachScraper(BaseScraper):
    """Scraper for Ruebenach fire department"""

    def __init__(self):
        super().__init__()

    def scrape(self):
        #skip