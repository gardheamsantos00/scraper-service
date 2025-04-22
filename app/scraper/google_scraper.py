import logging
from app.services.database_service import DatabaseService
from app.scraper.playwright_scraper import PlaywrightScraperService

logger = logging.getLogger("scraper")

class GoogleScraper:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.scraper_service = PlaywrightScraperService()

    async def scrape_and_store(self, query: str, location: str, max_pages: int = 1):
        logger.info(f"🔎 Buscando por '{query}' em '{location}', páginas: {max_pages}")

        # Prepara o termo de busca (buscando redes sociais)
        search_query = f'{query} {location} site:instagram.com OR site:facebook.com OR site:linkedin.com'

        # Faz o scraping de forma assíncrona
        scraped_data = await self.scraper_service.scrape_google(search_query, max_pages)

        leads = []

        for item in scraped_data:
            lead = {
                "name": item.get("title"),
                "social_link": item.get("url"),
                "email": None,
                "phone": None,
                "city": location.split("-")[0] if "-" in location else location,
                "state": location.split("-")[1] if "-" in location else None
            }

            leads.append(lead)

        if leads:
            self.db_service.insert_many("leads", leads)
        
        return leads

    def run(self, query: str, location: str, max_pages: int = 1):
        """Modo síncrono (para testes locais)"""
        import asyncio
        return asyncio.run(self.scrape_and_store(query, location, max_pages))
