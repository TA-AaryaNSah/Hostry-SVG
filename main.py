import asyncio
import os
import re
import uuid
import logging
import uvicorn
from pyrogram import Client, filters, types
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from contextlib import asynccontextmanager

# --- CONFIGS ---
API_ID = 32541562
API_HASH = "e37e4432298d5a5eb4a6e32c18804283"
BOT_TOKEN = "7886130082:AAE1IROKiE8rvDvX2aDK-En-2p_rnzkcX_Q"
MONGO_URI = "mongodb+srv://aaryansah954:QgDQRgyD7VUa7Eho@cluster0.wjo9zfm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
WEB_URL = "https://www.f2l.xalfh.dpdns.org"
ADMIN_ID = 8676822109
PORT = int(os.environ.get("PORT", 8080))

# --- DB & BOT INIT ---
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["stream_bot"]
files_db = db["files"]
settings_db = db["settings"]

bot = Client("ProBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.start()
    logging.info("Bot Started!")
    yield
    await bot.stop()

app = FastAPI(lifespan=lifespan)

# --- ADMIN DB HELPERS ---
async def get_s():
    s = await settings_db.find_one({"_id": "config"})
    return s or {"bin": -1003009926889, "fsub": None, "fsub_id": None}

# --- WEB SERVER ---
@app.get("/watch/{hash_val}/{filename}")
async def stream(hash_val: str, range: str = Header(None)):
    data = await files_db.find_one({"hash": hash_val})
    if not data: raise HTTPException(status_code=404)
    msg = await bot.get_messages(data["chat_id"], data["msg_id"])
    media = msg.document or msg.video
    
    start, end = 0, media.file_size - 1
    if range:
        m = re.search(r"bytes=(\d+)-(\d*)", range)
        if m:
            start = int(m.group(1))
            if m.group(2): end = int(m.group(2))
            
    return StreamingResponse(
        bot.stream_media(msg, offset=start, limit=end-start+1),
        status_code=206,
        headers={
            "Content-Range": f"bytes {start}-{end}/{media.file_size}",
            "Content-Length": str(end - start + 1),
            "Content-Type": getattr(media, "mime_type", "video/mp4")
        }
    )

# --- BOT HANDLERS ---
@bot.on_message(filters.command("settings") & filters.user(ADMIN_ID))
async def settings_menu(c, m):
    btn = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("➕ Add BIN Channel", callback_data="add_bin")],
        [types.InlineKeyboardButton("📢 Set FSub", callback_data="set_fsub")]
    ])
    await m.reply("🛠 **Admin Panel:**", reply_markup=btn)

@bot.on_callback_query()
async def cb(c, q):
    if q.data == "add_bin":
        await q.message.edit("Send new BIN ID:")
        res = await c.listen(chat_id=q.message.chat.id)
        await settings_db.update_one({"_id": "config"}, {"$set": {"bin": int(res.text)}}, upsert=True)
        await q.message.reply("✅ BIN Updated!")

@bot.on_message(filters.private & (filters.document | filters.video))
async def handle(c, m):
    s = await get_s()
    # Check FSub logic
    if s.get("fsub_id"):
        try:
            await c.get_chat_member(s["fsub_id"], m.from_user.id)
        except:
            return await m.reply("❌ Join channel first!", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("Join", url=s["fsub"])]]))
    
    msg = await m.reply("⏳ Generating link...")
    h = uuid.uuid4().hex[:8]
    await files_db.insert_one({"hash": h, "chat_id": m.chat.id, "msg_id": m.id})
    
    # Forward to BIN
    try: await m.forward(s["bin"])
    except: pass
    
    link = f"{WEB_URL}/watch/{h}/{m.document.file_name if m.document else 'video.mp4'}?hash={h}"
    await msg.edit(f"✅ Link: {link}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
