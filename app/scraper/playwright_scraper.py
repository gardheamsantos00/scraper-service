import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from app.config.settings import scraper_settings

class PlaywrightScraperService:
    def __init__(self):
        self.headless = scraper_settings.HEADLESS_MODE
        self.user_agent = scraper_settings.USER_AGENT

    async def is_captcha_page(self, page):
        try:
            content = await page.content()
            if "recaptcha" in content.lower() or "unusual traffic" in content.lower():
                return True
            return False
        except Exception as e:
            print(f"[CAPTCHA CHECK ERROR]: {e}")
            return False

    async def scrape_google(self, search_query: str, max_pages: int = 1):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=self.headless)
        context = await browser.new_context(user_agent=self.user_agent)
        page = await context.new_page()
        results = []

        try:
            page_num = 0
            while page_num < max_pages:
                url = f"https://www.google.com/search?q={search_query}&start={page_num * 10}"
                await page.goto(url)
                await page.wait_for_selector("div.MjjYud", timeout=5000)

                # Verifica se é CAPTCHA
                if await self.is_captcha_page(page):
                    print("⚠️ CAPTCHA detectado! Abortando scraping.")
                    break

                # Coletar os resultados
                result_boxes = await page.query_selector_all("div.MjjYud")
                for box in result_boxes:
                    title_element = await box.query_selector("h3")
                    link_element = await box.query_selector("a")
                    description_element = await box.query_selector("div.VwiC3b")

                    title = await title_element.inner_text() if title_element else None
                    link = await link_element.get_attribute("href") if link_element else None
                    description = await description_element.inner_text() if description_element else None

                    if title and link:
                        results.append({
                            "title": title,
                            "url": link,
                            "description": description
                        })

                # Tenta clicar no botão "Próxima página"
                try:
                    next_button = await page.query_selector('a#pnnext')
                    if next_button:
                        await next_button.click()
                        await asyncio.sleep(random.uniform(2, 5))  # Simula comportamento humano
                    else:
                        print("🚫 Sem mais páginas disponíveis.")
                        break
                except PlaywrightTimeoutError:
                    print("🚫 Timeout procurando botão de próxima página.")
                    break

                page_num += 1

        except Exception as e:
            print(f"[ERRO NO SCRAPING]: {e}")
        finally:
            await browser.close()
            await playwright.stop()

        return results

    def run_scrape_google(self, search_query: str, max_pages: int = 1):
        return asyncio.run(self.scrape_google(search_query, max_pages))
