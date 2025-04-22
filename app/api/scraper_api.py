from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.database_service import DatabaseService
from app.scraper.google_scraper import GoogleScraper
from app.config.settings import db_settings
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Inicializar app FastAPI
app = FastAPI(title="Scraper API - MDM-IMOBILL")

# Conectar ao banco
db_service = DatabaseService(db_settings.URI, db_settings.DB_NAME)

# Model para parâmetros da requisição
class ScraperParams(BaseModel):
    query: str
    location: str
    max_pages: int = 1

@app.post("/scrape/google")
def scrape_google(params: ScraperParams):
    try:
        logging.info(f"Recebida requisição: query={params.query}, location={params.location}, max_pages={params.max_pages}")

        google_scraper = GoogleScraper(db_service)
        google_scraper.run(query=params.query, location=params.location, max_pages=params.max_pages)

        logging.info(f"Scraping finalizado com sucesso para '{params.query}' em '{params.location}'")
        return {"status": "success", "message": "Scraping finalizado."}
    
    except Exception as e:
        logging.error(f"Erro durante scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
