from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.database_service import DatabaseService
from app.scraper.google_scraper import GoogleScraper
from app.config.settings import db_settings
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scraper_api")

# Inicializar app FastAPI
app = FastAPI(
    title="Scraper API - MDM-IMOBILL",
    description="API para gerenciar scraping de dados para o projeto MDM-IMOBILL",
    version="1.0.0"
)

# Conectar ao banco
db_service = DatabaseService(db_settings.URI, db_settings.DB_NAME)

# Instância única para reuso e controle de ciclo de vida
google_scraper = GoogleScraper(db_service)

# Model para parâmetros da requisição
class ScraperParams(BaseModel):
    query: str
    location: str
    max_pages: int = 1


@app.on_event("startup")
async def startup_event():
    logger.info("🔧 Iniciando aplicação e scraper...")
    await google_scraper.init_browser()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🧹 Encerrando scraper e liberando recursos...")
    await google_scraper.close_browser()


@app.post("/scrape/google", summary="Executar scraping no Google", tags=["Scraping"])
async def scrape_google(params: ScraperParams):
    try:
        logger.info(f"📥 Requisição recebida: query='{params.query}', location='{params.location}', max_pages={params.max_pages}")

        results = await google_scraper.run(query=params.query, location=params.location, max_pages=params.max_pages)

        logger.info(f"✅ Scraping finalizado para '{params.query}' em '{params.location}' - {len(results)} resultados encontrados.")

        return {
            "status": "success",
            "message": f"Scraping finalizado para '{params.query}' em '{params.location}'.",
            "results_count": len(results),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"❌ Erro durante scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno durante scraping: {str(e)}")


@app.get("/scrape/history", summary="Listar queries executadas", tags=["Scraping"])
async def list_query_history():
    return {
        "executed_queries": google_scraper.query_log
    }
