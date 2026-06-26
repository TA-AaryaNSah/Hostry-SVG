from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://asvm:incorrectasvm@cluster0.v2z8vnw.mongodb.net/?appName=Cluster0"

client = AsyncIOMotorClient(MONGO_URL)
db = client["FileStreamBot"]

# Naya collection taaki purane error wale links clash na karein
files_col = db["files_v2"] 
users_col = db["users"]

# ---- FILE FUNCTIONS (Alag Concept: Ab File ID save hoga) ----
async def save_file(unique_id, file_id, file_name, file_size):
    await files_col.insert_one({
        "_id": unique_id, 
        "file_id": file_id, 
        "file_name": file_name, 
        "file_size": file_size
    })

async def get_file(unique_id):
    return await files_col.find_one({"_id": unique_id})

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
