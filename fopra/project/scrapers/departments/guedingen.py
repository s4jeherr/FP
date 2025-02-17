from datetime import datetime
from typing import List
from .basescraper import BaseScraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import logging

class GuedingenScraper(BaseScraper):
    """Scraper for Güdingen fire department"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def scrape(self):
        years = list(range(2023, 2024))
        base_url = "https://www.feuerwehr-guedingen.de/einsatzuebersicht-"

        d = {"ReportText": []}
        df = pd.DataFrame(data=d)

        for year in years:
            url = f"{base_url}{year}/"
            response = requests.get(url)

            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve {url}: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'einsatzverwaltung-reportlist'})

            if not table:
                self.logger.warning(f"No table found for {year}.")
                continue

            link_elements = []
            for row in table.find_all('tr', class_="report"):
                #self.logger.info(f"Report: {row}")c
                cell = row.find_all('td')[0]
                link = cell.find('a')
                if link and 'href' in link.attrs:
                    link_elements.append(link['href'])

            for link_url in link_elements:
                #self.logger.info(f"Report URLs: {link_url}")
                try:
                    article = Article(link_url)
                    article.download()
                    article.parse()
                    df = pd.concat([df, pd.DataFrame({"ReportText": [article.text]})], ignore_index=True)

                except Exception as e:
                    self.logger.exception(f"Failed to extract text from {link_url}: {e}")
        return df