import asyncio
import random
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from app.config.settings import scraper_settings

# Configura Logger
logger = logging.getLogger("scraper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PlaywrightScraperService:
    def __init__(self):
        self.headless = scraper_settings.HEADLESS_MODE
        self.user_agent = scraper_settings.USER_AGENT
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    async def _init_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        if not self.context:
            self.context = await self.browser.new_context(user_agent=self.user_agent)
        if not self.page:
            self.page = await self.context.new_page()

    async def close_browser(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def is_captcha_page(self):
        try:
            content = await self.page.content()
            if "recaptcha" in content.lower() or "unusual traffic" in content.lower():
                logger.warning("⚠️ CAPTCHA detectado!")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar CAPTCHA: {e}")
            return False

    async def _extract_result_data(self, box):
        try:
            title_element = await box.query_selector("h3")
            link_element = await box.query_selector("a")
            description_element = await box.query_selector("div.VwiC3b")  # Descrição em destaque

            title = await title_element.inner_text() if title_element else None
            link = await link_element.get_attribute("href") if link_element else None
            description = await description_element.inner_text() if description_element else None

            if title and link:
                return {
                    "title": title.strip(),
                    "url": link.strip(),
                    "description": description.strip() if description else None
                }
        except Exception as e:
            logger.error(f"Erro ao extrair dados de resultado: {e}")
        return None

    async def scrape_google(self, search_query: str, max_pages: int = 1):
        await self._init_browser()

        results = []
        page_num = 0

        try:
            while page_num < max_pages:
                url = f"https://www.google.com/search?q={search_query}&start={page_num}"
                logger.info(f"🔎 Buscando página {page_num + 1}: {url}")

                try:
                    await self.page.goto(url)
                   #varTemp = await self.page.wait_for_selector("div#dURPMd", timeout=15000)  # Aguarda a área principal
                   #logger.warning("⚠️ varTemp LOG: ", varTemp)
                except PlaywrightTimeoutError:
                    logger.warning("⚠️ Timeout esperando resultados. Pulando página.")
                    break

                if await self.is_captcha_page():
                    logger.error("❌ CAPTCHA detectado! Encerrando scraping.")
                    break

                # Agora varre dentro da área mais segura (center_col)
                center_col = await self.page.query_selector("div#dURPMd")
                if not center_col:
                    logger.warning("⚠️ Não encontrou a área de resultados (center_col).")
                    break

                result_boxes = await center_col.query_selector_all("div.dURPMd")  # Dentro da área center_col
                for box in result_boxes:
                    data = await self._extract_result_data(box)
                    if data:
                        results.append(data)

                # Tenta clicar no botão "próxima página"
                try:
                    next_button = await self.page.query_selector('a#pnnext')
                    if next_button:
                        await next_button.click()
                        await asyncio.sleep(random.uniform(2, 5))  # Delay humano
                    else:
                        logger.info("🚫 Sem mais páginas disponíveis.")
                        break
                except PlaywrightTimeoutError:
                    logger.warning("⚠️ Timeout tentando clicar no botão próxima página.")
                    break

                page_num += 1

        except Exception as e:
            logger.error(f"[ERRO NO SCRAPING]: {e}")

        return results

    def run_scrape_google(self, search_query: str, max_pages: int = 1):
        return asyncio.run(self.scrape_google(search_query, max_pages))
