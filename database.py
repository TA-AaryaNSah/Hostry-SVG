from motor.motor_asyncio import AsyncIOMotorClient

# Tera MongoDB URL yahan hardcode kar diya hai
MONGO_URL = "mongodb+srv://asvm:incorrectasvm@cluster0.v2z8vnw.mongodb.net/?appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URL)
db = client["FileStreamBot"]
files_col = db["files"]
users_col = db["users"]

# ---- FILE FUNCTIONS ----
async def save_file(unique_id, message_id):
    await files_col.insert_one({"_id": unique_id, "message_id": message_id})

async def get_file(unique_id):
    result = await files_col.find_one({"_id": unique_id})
    if result:
        return result.get("message_id")
    return None

# ---- USER FUNCTIONS ----
async def add_user(user_id):
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id})

async def get_all_users():
    return await users_col.find().to_list(length=None)

# ---- STATS FUNCTION ----
async def get_stats():
    total_users = await users_col.count_documents({})
    total_files = await files_col.count_documents({})
    return total_users, total_files
