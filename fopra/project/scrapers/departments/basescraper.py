from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from services.custom_llm import CustomLLMService

class BaseScraper(ABC):
    """Base class for fire department scrapers"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_soup(self, url: str) -> BeautifulSoup:
        """Fetch and parse URL content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            raise

    @abstractmethod
    def scrape(self) -> list:
        """Implement scraping logic in derived classes"""
        pass