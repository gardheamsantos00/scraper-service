from app.scraper.google_scraper import GoogleScraper
from app.services.database_service import DatabaseService
from app.config import settings

def main():
    print("🚀 Inicializando Scraper Service...")

    # Inicializa banco de dados
    db_service = DatabaseService(settings.MONGO_URI, settings.MONGO_DB_NAME)

    # Inicializa o Scraper
    google_scraper = GoogleScraper(db_service)

    # Executa uma busca de teste
    query = "Arquiteto"
    location = "Curitiba"
    google_scraper.run(query=query, location=location, max_pages=5)

if __name__ == "__main__":
    main()
