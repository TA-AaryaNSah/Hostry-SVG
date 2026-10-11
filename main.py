import asyncio
import sys

# --- CRITICAL EVENT LOOP FIX FOR PYTHON 3.14+ ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ------------------------------------------------

import os
import re
import math
import uuid
import urllib.parse
import logging
from aiohttp import web
from pyrogram import Client, filters, types
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient

# --- CONFIGURATIONS ---
API_ID = 1000000
API_HASH = "e37e4432298d5a5eb4a6e32c18804283"
BOT_TOKEN = "BOT_TOKEN_PASTE_HERE"
MONGO_URI = "MONGO_DB_CLUSTER_URL"
WEB_URL = "RENDER_OR_KOYEB_URL" # Ensure no trailing slash
ADMIN_ID = 8676822109
PORT = int(os.environ.get("PORT", 8080))

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["stream_bot_pro"]
files_db = db["files"]
users_db = db["users"]
settings_db = db["settings"]

bot = Client("ProStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# --- DATABASE HELPERS ---
async def get_admin_settings():
    config = await settings_db.find_one({"_id": "admin_config"})
    if not config:
        config = {"bin_channel": None, "fsub_channels": []}
        await settings_db.insert_one({"_id": "admin_config", **config})
    return config

async def update_settings(key, value):
    await settings_db.update_one({"_id": "admin_config"}, {"$set": {key: value}}, upsert=True)

def format_size(bytes_size):
    if bytes_size >= 1024 * 1024 * 1024: return f"{bytes_size / (1024 ** 3):.2f} GB"
    return f"{bytes_size / (1024 ** 2):.2f} MB"

def get_mime_type(filename):
    ext = filename.lower().split('.')[-1]
    mimes = {"mkv": "video/x-matroska", "mp4": "video/mp4", "webm": "video/webm", "avi": "video/x-msvideo"}
    return mimes.get(ext, "application/octet-stream")

# --- TELEGRAM BOT LOGIC ---

@bot.on_message(filters.command("start") & filters.private)
async def start_command(c: Client, m: types.Message):
    await users_db.update_one({"_id": m.from_user.id}, {"$set": {"name": m.from_user.first_name}}, upsert=True)
    text = (
        f"👋 **Welcome, {m.from_user.first_name}!**\n\n"
        "I am an advanced High-Speed File to Link Bot. Send me any file or video, "
        "and I will generate an instant stream & download link for you! 🚀"
    )
    await m.reply_text(text)

@bot.on_message(filters.command("settings") & filters.user(ADMIN_ID))
async def settings_panel(c: Client, m: types.Message):
    config = await get_admin_settings()
    bin_ch = config.get("bin_channel", "Not Set")
    fsubs = config.get("fsub_channels", [])
    
    text = f"🛠 **Advanced Admin Control Panel**\n\n"
    text += f"📂 **Current BIN Channel:** `{bin_ch}`\n"
    text += f"📢 **Active FSub Channels:** `{len(fsubs)} / 5`\n\n"
    text += "Use the buttons below to manage your bot settings."

    buttons = [
        [types.InlineKeyboardButton("➕ Set BIN Channel", callback_data="help_bin")],
        [types.InlineKeyboardButton("📢 Add FSub Channel", callback_data="help_fsub"),
         types.InlineKeyboardButton("🗑 Clear All FSubs", callback_data="clear_fsub")]
    ]
    await m.reply_text(text, reply_markup=types.InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.user(ADMIN_ID))
async def callback_handlers(c: Client, q: types.CallbackQuery):
    if q.data == "help_bin":
        await q.answer("To set a BIN channel, send: /setbin -100xxxxxxxx", show_alert=True)
    elif q.data == "help_fsub":
        await q.answer("To add an FSub, send: /addfsub -100xxxxxxxx https://t.me/yourlink", show_alert=True)
    elif q.data == "clear_fsub":
        await update_settings("fsub_channels", [])
        await q.message.edit_text("✅ **All Force Subscribe channels have been cleared!**")

@bot.on_message(filters.command("setbin") & filters.user(ADMIN_ID))
async def set_bin_cmd(c: Client, m: types.Message):
    if len(m.command) < 2: return await m.reply("⚠️ Usage: `/setbin -100xxxxxxxx`")
    try:
        await update_settings("bin_channel", int(m.command[1]))
        await m.reply("✅ **BIN Channel successfully updated!**")
    except ValueError:
        await m.reply("❌ **Invalid ID! Must be a number.**")

@bot.on_message(filters.command("addfsub") & filters.user(ADMIN_ID))
async def add_fsub_cmd(c: Client, m: types.Message):
    if len(m.command) < 3: return await m.reply("⚠️ Usage: `/addfsub -100xxxxxxxx https://t.me/link`")
    config = await get_admin_settings()
    fsubs = config.get("fsub_channels", [])
    
    if len(fsubs) >= 5:
        return await m.reply("❌ **Maximum limit reached! You can only add up to 5 FSub channels.**")
        
    try:
        new_fsub = {"id": int(m.command[1]), "link": m.command[2]}
        fsubs.append(new_fsub)
        await update_settings("fsub_channels", fsubs)
        await m.reply(f"✅ **FSub Channel Added Successfully!**\n\nTotal Active FSubs: `{len(fsubs)}/5`")
    except ValueError:
        await m.reply("❌ **Invalid ID! Channel ID must be a number.**")

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def file_handler(c: Client, m: types.Message):
    await users_db.update_one({"_id": m.from_user.id}, {"$set": {"name": m.from_user.first_name}}, upsert=True)
    config = await get_admin_settings()
    
    # Check FSub status
    fsubs = config.get("fsub_channels", [])
    not_joined = []
    
    for fsub in fsubs:
        try:
            member = await c.get_chat_member(fsub["id"], m.from_user.id)
            if member.status.name in ["LEFT", "BANNED", "KICKED"]:
                not_joined.append(fsub)
        except UserNotParticipant:
            not_joined.append(fsub)
        except Exception:
            pass # Ignore if bot is not admin in that channel

    if not_joined:
        buttons = [[types.InlineKeyboardButton(f"📢 Join Channel {i+1}", url=ch["link"])] for i, ch in enumerate(not_joined)]
        return await m.reply_text(
            "❌ **Access Denied!**\n\nYou must join our official channels to use this bot. Join using the buttons below, then send your file again.",
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )

    msg = await m.reply_text("⏳ **Securing and generating links...**")
    
    # Forward to BIN Channel
    bin_ch = config.get("bin_channel")
    if bin_ch:
        try:
            await m.forward(bin_ch)
        except Exception as e:
            logging.error(f"BIN Forward Error: {e}")

    file = m.document or m.video or m.audio
    file_id = file.file_id
    file_name = getattr(file, "file_name", "Video.mp4")
    file_size = file.file_size
    
    # Generate Advanced Hash
    hash_val = uuid.uuid4().hex[:10]
    
    await files_db.insert_one({
        "hash": hash_val,
        "file_id": file_id,
        "file_name": file_name,
        "file_size": file_size
    })
    
    safe_name = urllib.parse.quote(file_name)
    download_url = f"{WEB_URL}/{hash_val}/{safe_name}?hash={hash_val}"
    watch_url = f"{WEB_URL}/watch/{hash_val}/{safe_name}?hash={hash_val}"
    
    text = (
        f"✅ **Link Successfully Generated!**\n\n"
        f"📂 **File:** `{file_name}`\n"
        f"📦 **Size:** `{format_size(file_size)}`\n\n"
        f"📥 **Download Link:**\n`{download_url}`\n\n"
        f"🖥 **Watch Online:**\n`{watch_url}`"
    )
    
    btns = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton("⬇️ Download Link", url=download_url),
         types.InlineKeyboardButton("📺 Watch Online", url=watch_url)]
    ])
    await msg.edit_text(text, reply_markup=btns, disable_web_page_preview=True)

# --- AIOHTTP WEB SERVER & STREAM LOGIC ---

async def keep_alive_handler(request):
    return web.Response(text="Bot and Server are Active 24/7!", status=200)

async def web_player_handler(request):
    hash_val = request.match_info.get("hash")
    file_name = request.match_info.get("filename", "Video")
    
    safe_name = urllib.parse.quote(file_name)
    stream_url = f"/{hash_val}/{safe_name}?hash={hash_val}"
    mime = get_mime_type(file_name)
    
    html = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name}</title>
    <style>
        body {{ margin:0; padding:0; background:#0f0f0f; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; color:#fff; font-family:sans-serif; }}
        .box {{ width:90%; max-width:800px; background:#1a1a1a; padding:15px; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.6); }}
        h3 {{ margin-top:0; font-size:16px; word-wrap:break-word; text-align:center; color:#ddd; }}
        video {{ width:100%; border-radius:8px; background:#000; outline:none; }}
        .btns {{ display:flex; gap:10px; justify-content:center; margin-top:15px; flex-wrap:wrap; }}
        .btn {{ padding:10px 15px; color:#fff; text-decoration:none; font-weight:bold; border-radius:6px; transition:0.3s; }}
        .dl {{ background:#0088cc; }} .mx {{ background:#0055ff; }} .vlc {{ background:#ff8800; }}
        .btn:hover {{ opacity:0.8; }}
    </style></head><body>
    <div class="box"><h3>{file_name}</h3>
    <video controls controlsList="nodownload"><source src="{stream_url}" type="{mime}"></video>
    <div class="btns">
        <a href="{stream_url}" class="btn dl" download>⬇️ Download</a>
        <a href="intent:{stream_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_name};end" class="btn mx">📺 MX Player</a>
        <a href="vlc://{stream_url}" class="btn vlc">🧡 VLC</a>
    </div></div></body></html>
    """
    return web.Response(text=html, content_type="text/html")

async def file_stream_handler(request):
    hash_val = request.query.get("hash") or request.match_info.get("hash")
    if not hash_val: return web.Response(text="❌ Invalid Link!", status=400)
    
    file_data = await files_db.find_one({"hash": hash_val})
    if not file_data: return web.Response(text="❌ File not found or deleted!", status=404)
    
    file_size = file_data["file_size"]
    file_name = file_data["file_name"]
    mime_type = get_mime_type(file_name)
    
    range_header = request.headers.get("Range")
    start = 0
    end = file_size - 1
    status = 200

    if range_header:
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            if match.group(2): end = int(match.group(2))
            status = 206 

    limit = end - start + 1
    disposition = f'inline; filename="{file_name}"'

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(limit),
        "Content-Type": mime_type,
        "Content-Disposition": disposition
    }

    response = web.StreamResponse(status=status, headers=headers)
    await response.prepare(request)

    offset_chunk = start // 1048576 
    skip_bytes = start % 1048576

    try:
        async for chunk in bot.stream_media(file_data["file_id"], offset=offset_chunk):
            if skip_bytes:
                chunk = chunk[skip_bytes:]
                skip_bytes = 0
            if limit <= 0: break
            if len(chunk) > limit: chunk = chunk[:limit]
            
            await response.write(chunk)
            limit -= len(chunk)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Stream interrupted: {e}")
        
    return response

# --- EXECUTION ENGINE ---
async def start_all():
    # 1. Start Web Server (AIOHTTP is perfectly non-blocking)
    app = web.Application()
    app.router.add_get('/', keep_alive_handler) # Used for UptimeRobot
    app.router.add_get('/watch/{hash}/{filename}', web_player_handler)
    app.router.add_get('/{hash}/{filename}', file_stream_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"Web Server Running on Port {PORT}")

    # 2. Start Telegram Bot
    await bot.start()
    logging.info("Telegram Bot Started Successfully!")
    
    # Keep loop running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(start_all())
