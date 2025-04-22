import asyncio
from playwright.async_api import async_playwright
from app.config.settings import SCRAPER_USER_AGENT, HEADLESS_MODE

class PlaywrightScraperService:
    def __init__(self):
        self.headless = HEADLESS_MODE
        self.user_agent = SCRAPER_USER_AGENT

    async def scrape_google(self, search_query: str, max_pages: int = 1):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=self.headless)
        context = await browser.new_context(user_agent=self.user_agent)
        page = await context.new_page()

        results = []

        try:
            for page_number in range(max_pages):
                url = f"https://www.google.com/search?q={search_query}&start={page_number * 10}"
                await page.goto(url)
                await page.wait_for_selector("a h3", timeout=5000)

                h3_elements = await page.query_selector_all("a h3")
                for h3 in h3_elements:
                    parent = await h3.evaluate_handle("node => node.parentElement")
                    link = await parent.get_attribute('href')
                    title = await h3.inner_text()

                    if link and title:
                        results.append({"url": link, "title": title})

        except Exception as e:
            print(f"[ERRO NO SCRAPING] {e}")

        finally:
            await browser.close()
            await playwright.stop()

        return results

    def run_scrape_google(self, search_query: str, max_pages: int = 1):
        return asyncio.run(self.scrape_google(search_query, max_pages))
