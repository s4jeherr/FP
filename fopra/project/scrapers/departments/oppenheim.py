from datetime import datetime
from typing import List
from ..base import BaseScraper
from models.report import Report

class OppenheimScraper(BaseScraper):
    """Scraper for Oppenheim fire department"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ff-oppenheim.de"
        self.reports_url = f"{self.base_url}/einsaetze/"
    
    def scrape(self) -> List[Report]:
        reports = []
        try:
            soup = self.get_soup(self.reports_url)
            
            # Find all report articles
            report_articles = soup.find_all('article', class_='einsatz')
            
            for article in report_articles:
                try:
                    # Extract date
                    date_elem = article.find('span', class_='datum')
                    if not date_elem:
                        continue
                        
                    try:
                        date = datetime.strptime(date_elem.text.strip(), '%d.%m.%Y')
                    except ValueError:
                        continue
                    
                    # Extract title/type
                    title_elem = article.find('h2', class_='einsatz-titel')
                    einsatzart = title_elem.text.strip() if title_elem else "Unbekannt"
                    
                    # Extract location
                    location_elem = article.find('div', class_='einsatz-ort')
                    ort = location_elem.text.strip() if location_elem else "Unbekannt"
                    
                    # Extract duration
                    duration_elem = article.find('span', class_='einsatz-zeit')
                    dauer = duration_elem.text.strip() if duration_elem else "Unbekannt"
                    
                    # Extract units involved
                    units_elem = article.find('ul', class_='einheiten')
                    beteiligte = []
                    if units_elem:
                        unit_items = units_elem.find_all('li')
                        beteiligte = [unit.text.strip() for unit in unit_items]
                    
                    # Extract description
                    content_elem = article.find('div', class_='einsatz-text')
                    verlauf = content_elem.text.strip() if content_elem else ""
                    
                    # Create report
                    report = Report.create(
                        einsatzart=einsatzart,
                        ort=ort,
                        datum=date,
                        dauer=dauer,
                        beteiligte=beteiligte or ["Unbekannt"],
                        verlauf=verlauf
                    )
                    reports.append(report)
                    
                except Exception as e:
                    self.logger.error(f"Error parsing article: {str(e)}")
                    continue
                    
            self.logger.info(f"Scraped {len(reports)} reports from Oppenheim")
            
        except Exception as e:
            self.logger.error(f"Failed to scrape Oppenheim: {str(e)}")
            
        return reports