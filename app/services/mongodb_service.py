from pymongo import MongoClient
from app.config import settings

class MongoDBService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        mongo_uri = settings.MONGO_URI
        db_name = settings.MONGO_DB_NAME
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        """
        Retorna a coleção específica do MongoDB.
        """
        return self.db[collection_name]

    def insert_one(self, collection_name, document):
        """
        Insere um único documento em uma coleção.
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return result.inserted_id

    def find(self, collection_name, query):
        """
        Faz uma busca simples em uma coleção.
        """
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def find_one(self, collection_name, query):
        """
        Busca um único documento que satisfaça a consulta.
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def update_one(self, collection_name, query, update_values):
        """
        Atualiza um único documento que satisfaça a consulta.
        """
        collection = self.get_collection(collection_name)
        return collection.update_one(query, {'$set': update_values})

    def delete_one(self, collection_name, query):
        """
        Deleta um único documento que satisfaça a consulta.
        """
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

# Instância pronta para importar em outros módulos
mongodb_service = MongoDBService()
