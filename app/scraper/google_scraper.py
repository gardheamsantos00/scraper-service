import logging
import asyncio
from app.services.database_service import DatabaseService
from app.scraper.playwright_scraper import PlaywrightScraperService
from app.scraper.api_google_cse_scraper import GoogleCustomSearchService  # Novo import

logger = logging.getLogger("scraper")

class GoogleScraper:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.playwright_scraper = PlaywrightScraperService()
        self.cse_scraper = GoogleCustomSearchService()  # Instância da nova API

    async def scrape_and_store(self, query: str, location: str, max_pages: int = 1, use_cse_api: bool = False):
        logger.info(f"🔎 Iniciando scraping ({'CSE API' if use_cse_api else 'Playwright'}) para '{query}' em '{location}'")

        search_query = f'site:instagram.com OR site:facebook.com OR site:linkedin.com {query} {location} "@gmail.com" OR "@yahoo.com" OR "@hotmail.com" OR "@outlook.com" OR "@aol.com" OR "@yahoo.com.br"'

        if use_cse_api:
            scraped_data = await self.cse_scraper.scrape_google_cse(search_query, max_pages)
        else:
            scraped_data = await self.playwright_scraper.scrape_google(search_query, max_pages)

        leads = []
        for item in scraped_data:
            leads.append({
                "name": item.get("title"),
                "social_link": item.get("url"),
                "email": None,
                "phone": None,
                "city": location.split("-")[0] if "-" in location else location,
                "state": location.split("-")[1] if "-" in location else None
            })

        if leads:
            self.db_service.insert_many("leads", leads)

        return leads

    def run(self, query: str, location: str, max_pages: int = 1, use_cse_api: bool = False):
        return asyncio.run(self.scrape_and_store(query, location, max_pages, use_cse_api))
