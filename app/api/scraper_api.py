from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.database_service import DatabaseService
from app.scraper.google_scraper import GoogleScraper
from app.config.settings import db_settings
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scraper")

# Inicializar app FastAPI
app = FastAPI(title="Scraper API - MDM-IMOBILL")

# Banco de dados e scraper
db_service = DatabaseService(db_settings.URI, db_settings.DB_NAME)
google_scraper = GoogleScraper(db_service)

# Cache local para histórico (com TTL simulado)
import time
SCRAPE_CACHE = {}
CACHE_TTL_SECONDS = 3600  # 1 hora

# Modelo para parâmetros da requisição
class ScraperParams(BaseModel):
    query: str
    location: str
    max_pages: int = 1


@app.post("/scrape/google")
async def scrape_google(params: ScraperParams):
    try:
        key = f"{params.query.lower()}|{params.location.lower()}"
        now = time.time()

        # Verifica se já está no cache
        if key in SCRAPE_CACHE and now - SCRAPE_CACHE[key]["timestamp"] < CACHE_TTL_SECONDS:
            logger.info(f"[CACHE HIT] Retornando resultados em cache para {key}")
            return {
                "status": "cached",
                "results": SCRAPE_CACHE[key]["results"]
            }

        logger.info(f"Recebida requisição: query={params.query}, location={params.location}, max_pages={params.max_pages}")

        results = await google_scraper.scrape_and_store(
            query=params.query,
            location=params.location,
            max_pages=params.max_pages
        )

        # Armazena no cache local
        SCRAPE_CACHE[key] = {
            "timestamp": now,
            "results": results
        }

        logger.info(f"Scraping finalizado com sucesso para '{params.query}' em '{params.location}'")
        return {
            "status": "success",
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro durante scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/scrape/history")
def list_scrape_history():
    """Endpoint para listar os termos de scraping realizados recentemente"""
    history = [
        {
            "key": key,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["timestamp"])),
            "result_count": len(data["results"])
        }
        for key, data in SCRAPE_CACHE.items()
    ]
    return {"history": history}


@app.on_event("shutdown")
async def shutdown_event():
    """Fecha o browser Playwright ao encerrar a API"""
    logger.info("⛔ Finalizando aplicação e fechando navegador...")
    await google_scraper.scraper_service.close_browser()
