from motor.motor_asyncio import AsyncIOMotorClient

# Tera MongoDB URL yahan hardcode kar diya hai
MONGO_URL = "mongodb+srv://asvm:incorrectasvm@cluster0.v2z8vnw.mongodb.net/?appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URL)
db = client["FileStreamBot"]
collection = db["files"]

async def save_file(unique_id, message_id):
    await collection.insert_one({"_id": unique_id, "message_id": message_id})

async def get_file(unique_id):
    result = await collection.find_one({"_id": unique_id})
    if result:
        return result.get("message_id")
    return None
