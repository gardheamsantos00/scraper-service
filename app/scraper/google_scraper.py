class GoogleScraper:
    def __init__(self, db_service):
        self.db_service = db_service

    def run(self, query, location, max_pages=1):
        print(f"🔍 Buscando por '{query}' em '{location}', páginas: {max_pages}")
        # (Aqui no próximo passo implementamos de fato a lógica com Selenium/Scrapy)

        # Exemplo de salvamento:
        example_lead = {
            "name": "Exemplo Lead",
            "social_link": "https://instagram.com/exemplo",
            "email": "exemplo@gmail.com",
            "phone": "(41) 99999-9999",
            "city": "Curitiba",
            "state": "PR"
        }
        self.db_service.save_lead("leads", example_lead)
