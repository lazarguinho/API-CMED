from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017/cmed"
client = AsyncIOMotorClient(MONGO_URI)
db = client.cmed  # Banco de dados principal

def get_database():
    return db
