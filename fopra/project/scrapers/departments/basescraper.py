from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from models.report import Report
from services.custom_llm import CustomLLMService

class BaseScraper(ABC):
    """Base class for fire department scrapers"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.llm_service = CustomLLMService()
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
    
    def process_report(self, text: str, date: datetime) -> Report:
        """Process report text and create Report object"""
        try:
            # Try LLM analysis first
            llm_result = self.llm_service.analyze_report(text, date)
            return Report.create(**llm_result)
        except Exception as e:
            self.logger.warning(f"LLM analysis failed, creating basic report: {str(e)}")
            # Create basic report without LLM analysis
            return Report.create(
                einsatzart="Nicht klassifiziert",
                ort="Unbekannt",
                datum=date,
                dauer="Unbekannt",
                beteiligte=["Unbekannt"],
                verlauf=text
            )
    
    @abstractmethod
    def scrape(self) -> list:
        """Implement scraping logic in derived classes"""
        pass