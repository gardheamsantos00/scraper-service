import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "scraper_db")

# Configurações do Scraping
SCRAPER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Outras configurações
HEADLESS_MODE = True  # Para rodar o navegador sem abrir a janela
