import asyncio

# --- EVENT LOOP FIX ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import os
import re
import math
import uuid
import urllib.parse
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient

from database import save_file, get_file, add_user, get_all_users, get_stats

# --- CREDENTIALS ---
API_ID = 32541562
API_HASH = "e37e4432298d5a5eb4a6e32c18804283"
BOT_TOKEN = "8932447404:AAEnctZD5fzy90BDIVlqV1mmjXnyNb5qoxg"
DEFAULT_BIN_CHANNEL = -1003009926889 
ADMIN_ID = 8676822109 
WEB_URL = "https://www.f2l.xalfh.dpdns.org" # No trailing slash
PORT = int(os.environ.get("PORT", 8080))
MONGO_URI = "mongodb+srv://aaryansah954:QgDQRgyD7VUa7Eho@cluster0.wjo9zfm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

bot = Client("StreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- DYNAMIC SETTINGS DB ---
db_client = AsyncIOMotorClient(MONGO_URI)
settings_db = db_client["stream_bot"]["settings"]

async def get_fsub():
    data = await settings_db.find_one({"_id": "fsub"})
    return data if data else {"link": None, "channel_id": None}

async def get_bin():
    data = await settings_db.find_one({"_id": "bin"})
    return data["channel_id"] if data else DEFAULT_BIN_CHANNEL

async def check_fsub(client, user_id):
    fsub = await get_fsub()
    if not fsub["channel_id"]:
        return True
    try:
        member = await client.get_chat_member(fsub["channel_id"], user_id)
        if member.status.name in ["LEFT", "BANNED", "KICKED"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True # Fallback if bot is not admin in the fsub channel

# --- UTILS ---
def format_size(bytes_size):
    if bytes_size >= 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
    return f"{bytes_size / (1024 * 1024):.2f} MB"

def get_mime_type(filename):
    filename = filename.lower()
    if filename.endswith(".mkv"): return "video/x-matroska"
    if filename.endswith(".mp4"): return "video/mp4"
    if filename.endswith(".webm"): return "video/webm"
    if filename.endswith(".avi"): return "video/x-msvideo"
    return "application/octet-stream"

# ---- BOT COMMANDS LOGIC ----

@bot.on_message(filters.command("start") & filters.private)
async def start_msg(client: Client, message: Message):
    await add_user(message.from_user.id)
    text = (
        "👋 **Hello! Welcome to the Fast Stream Bot.**\n\n"
        "I can instantly convert your Telegram videos and files into **High-Speed Download & Streaming Links**.\n\n"
        "🚀 **Simply forward or send any video/file to get started!**"
    )
    await message.reply_text(text)

@bot.on_message(filters.command("add_bin") & filters.user(ADMIN_ID))
async def add_bin_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** `/add_bin -100xxxxxxxx`")
    try:
        new_bin = int(message.command[1])
        await settings_db.update_one({"_id": "bin"}, {"$set": {"channel_id": new_bin}}, upsert=True)
        await message.reply(f"✅ **BIN Channel successfully updated to:** `{new_bin}`")
    except ValueError:
        await message.reply("❌ **Invalid Channel ID format!**")

@bot.on_message(filters.command("fsub") & filters.user(ADMIN_ID))
async def set_fsub_cmd(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply("⚠️ **Usage:** `/fsub https://t.me/yourlink -100xxxxxxxx`\n\nTo disable FSub, use: `/fsub off off`")
    
    link = message.command[1]
    channel_id = message.command[2]
    
    if link.lower() == "off":
        await settings_db.update_one({"_id": "fsub"}, {"$set": {"link": None, "channel_id": None}}, upsert=True)
        return await message.reply("✅ **Force Subscribe has been Disabled!**")
        
    try:
        channel_id = int(channel_id)
        await settings_db.update_one({"_id": "fsub"}, {"$set": {"link": link, "channel_id": channel_id}}, upsert=True)
        await message.reply(f"✅ **Force Subscribe successfully activated!**\n\n🔗 **Link:** {link}\n🆔 **Channel ID:** `{channel_id}`")
    except ValueError:
        await message.reply("❌ **Invalid Channel ID format!**")

@bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def bot_stats(client: Client, message: Message):
    msg = await message.reply("⏳ Fetching stats...")
    users, files = await get_stats()
    await msg.edit(f"📊 **Database Analytics**\n\n👥 Total Users: `{users}`\n📂 Total Files: `{files}`")

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_msg(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message with `/broadcast` to send it to all users.")
    
    msg = await message.reply("⏳ Broadcasting message...")
    users = await get_all_users()
    success, failed = 0, 0
    
    for user in users:
        try:
            await message.reply_to_message.copy(user["_id"])
            success += 1
            await asyncio.sleep(0.1)
        except:
            failed += 1
            
    await msg.edit(f"✅ **Broadcast Complete!**\n\n🟢 Successful: `{success}`\n🔴 Failed: `{failed}`")

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def handle_files(client: Client, message: Message):
    await add_user(message.from_user.id)
    
    # 1. Check Force Subscribe
    fsub = await get_fsub()
    if fsub["channel_id"]:
        is_participant = await check_fsub(client, message.from_user.id)
        if not is_participant:
            btn = [[InlineKeyboardButton("📢 Join Updates Channel", url=fsub["link"])]]
            return await message.reply(
                "❌ **Access Denied!**\n\nYou must join our official channel to use this bot. Join now and try sending the file again.", 
                reply_markup=InlineKeyboardMarkup(btn)
            )

    msg = await message.reply_text("⏳ Generating secure hash link...")
    
    try:
        # 2. Forward to BIN Channel (Silently ignore errors for user)
        bin_id = await get_bin()
        try:
            await message.forward(bin_id)
        except Exception as fwd_err:
            print(f"Failed to forward to BIN: {fwd_err}")
            pass 
        
        # 3. Process File Details
        file = message.document or message.video or message.audio
        file_id = file.file_id  
        file_name = getattr(file, "file_name", "Video_File.mp4")
        file_size = file.file_size
        
        # Generate short unique hash
        hash_val = uuid.uuid4().hex[:8]
        
        # Save to DB
        await save_file(hash_val, file_id, file_name, file_size)
        
        safe_file_name = urllib.parse.quote(file_name)
        
        # Exact Requested URL Format
        download_link = f"{WEB_URL}/{hash_val}/{safe_file_name}?hash={hash_val}"
        watch_link = f"{WEB_URL}/watch/{hash_val}/{safe_file_name}?hash={hash_val}"
        
        text = (
            f"✅ **Link Successfully Generated!**\n\n"
            f"📂 **File Name:** `{file_name}`\n"
            f"📦 **Size:** `{format_size(file_size)}`\n\n"
            f"📥 **Download Link:**\n`{download_link}`\n\n"
            f"🖥 **Watch Online:**\n`{watch_link}`"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬇️ Download Link", url=download_link), InlineKeyboardButton("📺 Watch Online", url=watch_link)]
        ])
        
        await msg.edit_text(text, reply_markup=buttons, disable_web_page_preview=True)
        
    except Exception as e:
        await msg.edit_text(f"❌ **An Error Occurred:** `{e}`")

# ---- WEB SERVER: HTML PLAYER LOGIC ----
async def watch_handler(request):
    file_name = request.match_info.get("filename", "Video")
    hash_val = request.match_info.get("hash")
    query_hash = request.query.get("hash")
    
    final_hash = hash_val or query_hash
    if not final_hash:
        return web.Response(text="❌ Invalid Link: Hash is missing!", status=400)
    
    safe_file_name = urllib.parse.quote(file_name)
    stream_url = f"/{final_hash}/{safe_file_name}?hash={final_hash}"
    mime_type = get_mime_type(file_name)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{file_name}</title>
        <style>
            body {{ margin: 0; padding: 0; background-color: #0f0f0f; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; color: #fff; font-family: sans-serif; }}
            .player-container {{ width: 90%; max-width: 850px; background: #1a1a1a; padding: 15px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); }}
            h3 {{ margin-top: 0; font-size: 16px; word-wrap: break-word; color: #ccc; text-align: center; }}
            video {{ width: 100%; border-radius: 8px; outline: none; background: #000; }}
            .buttons {{ display: flex; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }}
            .btn {{ padding: 10px 20px; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; transition: 0.3s; text-align: center; }}
            .dl-btn {{ background: #0088cc; }} .dl-btn:hover {{ background: #006699; }}
            .mx-btn {{ background: #0055ff; }} .mx-btn:hover {{ background: #0044cc; }}
            .vlc-btn {{ background: #ff8800; }} .vlc-btn:hover {{ background: #cc6600; }}
        </style>
    </head>
    <body>
        <div class="player-container">
            <h3>{file_name}</h3>
            <video controls controlsList="nodownload">
                <source src="{stream_url}" type="{mime_type}">
            </video>
            <div class="buttons">
                <a href="{stream_url}" class="btn dl-btn" download>⬇️ Download</a>
                <a href="intent:{stream_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_name};end" class="btn mx-btn">📺 Play in MX Player</a>
                <a href="vlc://{stream_url}" class="btn vlc-btn">🧡 Play in VLC</a>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")

# ---- WEB SERVER: FAST STREAMING LOGIC ----
async def stream_handler(request):
    try:
        hash_val = request.match_info.get("hash")
        query_hash = request.query.get("hash")
        final_hash = hash_val or query_hash
        
        if not final_hash:
            return web.Response(text="❌ Hash missing in URL!", status=400)
            
        file_data = await get_file(final_hash)
        if not file_data:
            return web.Response(text="❌ File not found or link has expired!", status=404)
            
        file_id = file_data["file_id"]
        file_name = file_data["file_name"]
        file_size = file_data["file_size"]
        mime_type = get_mime_type(file_name)
        
        range_header = request.headers.get("Range")
        start = 0
        end = file_size - 1
        status = 200

        if range_header:
            match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if match:
                start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))
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

        chunk_size = 1048576 
        offset_chunk = start // chunk_size
        skip_bytes = start % chunk_size

        try:
            async for chunk in bot.stream_media(file_id, offset=offset_chunk):
                if skip_bytes:
                    chunk = chunk[skip_bytes:]
                    skip_bytes = 0
                
                if limit <= 0:
                    break
                    
                if len(chunk) > limit:
                    chunk = chunk[:limit]
                    
                await response.write(chunk)
                limit -= len(chunk)
        except asyncio.CancelledError:
            pass 
            
        return response

    except Exception as e:
        print(f"Stream Error: {e}")
        return web.Response(text="❌ Server Error: File stream failed.", status=500)

# ---- APP RUNNER ----
async def start_services():
    await bot.start()
    print("Bot Started Successfully! Advanced Features Active.")
    
    app = web.Application()
    # Updated Web Routes to match your specific layout
    app.router.add_get('/watch/{hash}/{filename}', watch_handler)
    app.router.add_get('/{hash}/{filename}', stream_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web Server Started on Port {PORT}!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(start_services())
