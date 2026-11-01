import os
from pymongo import AsyncMongoClient
from procurement_ai_api.core.config import settings



class DatabaseManager:
    def __init__(self):
        self.client: AsyncMongoClient | None = None
        self.db = None

    async def connect(self):
        self.client = AsyncMongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]
        
        # Await the ping command
        await self.client.admin.command('ping')

    async def close(self):
        """Close the async MongoDB connection pool."""
        if self.client:
            await self.client.close()

    def get_db(self):
        """Retrieve the database instance."""
        if self.db is None:
            raise ConnectionError("Database is not connected. Call connect() first.")
        return self.db

db_manager = DatabaseManager()