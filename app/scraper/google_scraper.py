from app.services.database_service import DatabaseService
from app.scraper.services.playwright_scraper import PlaywrightScraperService

class GoogleScraper:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.scraper_service = PlaywrightScraperService()

    def run(self, query: str, location: str, max_pages: int = 1):
        print(f"🔎 Buscando por '{query}' em '{location}', páginas: {max_pages}")

        # Prepara o termo de busca
        search_query = f'{query} {location} site:instagram.com OR site:facebook.com OR site:linkedin.com'

        # Faz o scraping
        scraped_data = self.scraper_service.run_scrape_google(search_query, max_pages)

        for item in scraped_data:
            lead = {
                "name": item.get("title"),
                "social_link": item.get("url"),
                "email": None,
                "phone": None,
                "city": location.split("-")[0] if "-" in location else location,
                "state": location.split("-")[1] if "-" in location else None
            }

            # Salva o lead no banco
            self.db_service.save_lead("leads", lead)
