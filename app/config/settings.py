import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Configurações de Banco de Dados
class DatabaseSettings:
    URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("MONGO_DB_NAME", "scraper_db")

# Configurações de Scraping
class ScraperSettings:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"

# Outras configurações globais (se quiser adicionar depois)
class GeneralSettings:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # Ex: development, production

# Se quiser acessar rápido em outros lugares
db_settings = DatabaseSettings()
scraper_settings = ScraperSettings()
general_settings = GeneralSettings()
