from datetime import datetime
from typing import List
from basescraper import BaseScraper
from models.report import Report

class GuedingenScraper(BaseScraper):
    """Scraper for Güdingen fire department"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.feuerwehr-guedingen.de"
        self.archive_pattern = "/einsatzuebersicht-{year}/"

    def scrape(self) -> List[Report]:
        reports = []
        current_year = datetime.now().year

        # Scrape from 2019 to current year
        for year in range(2019, current_year + 1):
            try:
                url = f"{self.base_url}{self.archive_pattern.format(year=year)}"
                self.logger.info(f"Scraping: {url}")

                soup = self.get_soup(url)

                # Find all report containers
                report_containers = soup.find_all('article', class_='einsatz-bericht')

                for container in report_containers:
                    try:
                        # Extract date and time
                        date_elem = container.find('time', class_='einsatz-datum')
                        if not date_elem:
                            continue

                        date_str = date_elem.get('datetime') or date_elem.text.strip()
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                        except ValueError:
                            try:
                                date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')
                            except ValueError:
                                continue

                        # Extract title/type
                        title_elem = container.find('h2', class_='einsatz-titel')
                        einsatzart = title_elem.text.strip() if title_elem else "Unbekannt"

                        # Extract location
                        location_elem = container.find('div', class_='einsatz-ort')
                        ort = location_elem.text.strip() if location_elem else "Unbekannt"

                        # Extract duration
                        duration_elem = container.find('span', class_='einsatz-dauer')
                        dauer = duration_elem.text.strip() if duration_elem else "Unbekannt"

                        # Extract units involved
                        units_elem = container.find('div', class_='einsatz-einheiten')
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
                        self.logger.error(f"Error parsing report container: {str(e)}")
                        continue

            except Exception as e:
                self.logger.error(f"Error scraping year {year}: {str(e)}")
                continue

        self.logger.info(f"Total reports scraped: {len(reports)}")
        return reports