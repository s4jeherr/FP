from datetime import datetime
from typing import List
from ..base import BaseScraper
from models.report import Report

class RuebenachScraper(BaseScraper):
    """Scraper for Ruebenach fire department"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.feuerwehr-ruebenach.de"
        self.reports_url = f"{self.base_url}/einsaetze/"
    
    def scrape(self) -> List[Report]:
        reports = []
        try:
            soup = self.get_soup(self.reports_url)
            
            # Find all report containers
            report_containers = soup.find_all('div', class_='einsatz-container')
            
            for container in report_containers:
                try:
                    # Extract date
                    date_elem = container.find('span', class_='einsatz-datum')
                    if not date_elem:
                        continue
                        
                    try:
                        date = datetime.strptime(date_elem.text.strip(), '%d.%m.%Y')
                    except ValueError:
                        continue
                    
                    # Extract title/type
                    title_elem = container.find('h3', class_='einsatz-art')
                    einsatzart = title_elem.text.strip() if title_elem else "Unbekannt"
                    
                    # Extract location
                    location_elem = container.find('div', class_='einsatz-ort')
                    ort = location_elem.text.strip() if location_elem else "Unbekannt"
                    
                    # Extract duration
                    duration_elem = container.find('span', class_='einsatz-zeit')
                    dauer = duration_elem.text.strip() if duration_elem else "Unbekannt"
                    
                    # Extract units involved
                    units_elem = container.find('ul', class_='einsatz-kraefte')
                    beteiligte = []
                    if units_elem:
                        unit_items = units_elem.find_all('li')
                        beteiligte = [unit.text.strip() for unit in unit_items]
                    
                    # Extract description
                    content_elem = container.find('div', class_='einsatz-beschreibung')
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
                    self.logger.error(f"Error parsing container: {str(e)}")
                    continue
                    
            self.logger.info(f"Scraped {len(reports)} reports from Ruebenach")
            
        except Exception as e:
            self.logger.error(f"Failed to scrape Ruebenach: {str(e)}")
            
        return reports