from datetime import datetime
from typing import List
from ..base import BaseScraper
from models.report import Report

class PluwigScraper(BaseScraper):
    """Scraper for Pluwig-Gusterath fire department"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://feuerwehr-pluwig-gusterath.de"
        self.reports_url = f"{self.base_url}/einsaetze/"
    
    def scrape(self) -> List[Report]:
        reports = []
        try:
            soup = self.get_soup(self.reports_url)
            
            # Find all report articles
            report_articles = soup.find_all('article', class_='einsatzbericht')
            
            for article in report_articles:
                try:
                    # Extract date
                    date_elem = article.find('time', class_='einsatz-datum')
                    if not date_elem:
                        continue
                        
                    try:
                        date = datetime.strptime(date_elem.text.strip(), '%d.%m.%Y')
                    except ValueError:
                        continue
                    
                    # Extract title/type
                    title_elem = article.find('h2', class_='entry-title')
                    einsatzart = title_elem.text.strip() if title_elem else "Unbekannt"
                    
                    # Extract location from title or dedicated element
                    location_elem = article.find('span', class_='einsatz-ort')
                    if location_elem:
                        ort = location_elem.text.strip()
                    else:
                        # Try to extract location from title
                        title_parts = einsatzart.split(" in ")
                        ort = title_parts[1].strip() if len(title_parts) > 1 else "Unbekannt"
                    
                    # Extract duration
                    duration_elem = article.find('span', class_='einsatz-dauer')
                    dauer = duration_elem.text.strip() if duration_elem else "Unbekannt"
                    
                    # Extract units involved
                    units_elem = article.find('div', class_='einsatz-kraefte')
                    beteiligte = []
                    if units_elem:
                        unit_items = units_elem.find_all('li')
                        beteiligte = [unit.text.strip() for unit in unit_items]
                    
                    # Extract description
                    content_elem = article.find('div', class_='entry-content')
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
                    
            self.logger.info(f"Scraped {len(reports)} reports from Pluwig-Gusterath")
            
        except Exception as e:
            self.logger.error(f"Failed to scrape Pluwig-Gusterath: {str(e)}")
            
        return reports