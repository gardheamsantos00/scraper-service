from app.services.database_service import DatabaseService
from app.scraper.google_scraper import GoogleScraper
from app.config.settings import MONGO_URI, MONGO_DB_NAME

def main():
    # Inicializa serviço de banco
    db_service = DatabaseService(MONGO_URI, MONGO_DB_NAME)

    # Inicializa serviço de scraping
    google_scraper = GoogleScraper(db_service)

    # Parâmetros de exemplo
    query = "Arquiteto"
    location = "Curitiba-PR"
    max_pages = 1

    # Executa o scraping
    google_scraper.run(query=query, location=location, max_pages=max_pages)

if __name__ == "__main__":
    main()
