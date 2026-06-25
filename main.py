import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

import os
import re
import math
import uuid
import urllib.parse
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message
from database import save_file, get_file, add_user, get_all_users, get_stats

# --- TERE CREDENTIALS ---
API_ID = 32541562
API_HASH = "e37e4432298d5a5eb4a6e32c18804283"
BOT_TOKEN = "8932447404:AAGZ1I0ZLesk3DIZw-IVCtliPLd4O9HVFAA"
BIN_CHANNEL = -1002521835919

# 👉 YAHAN APNI TELEGRAM USER ID DAALNA (Without Quotes)
ADMIN_ID = 8676822109 

WEB_URL = os.environ.get("WEB_URL", "https://hostry-svg.onrender.com/") 
PORT = int(os.environ.get("PORT", 8080))

bot = Client("StreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def format_size(bytes_size):
    if bytes_size >= 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
    return f"{bytes_size / (1024 * 1024):.2f} MB"

# ---- BOT COMMANDS LOGIC ----

@bot.on_message(filters.command("start") & filters.private)
async def start_msg(client: Client, message: Message):
    await add_user(message.from_user.id) # User ko DB me save karo
    text = (
        "👋 Hello Bhai!\n\n"
        "Main ek **Ultra-Fast Stream Bot** hoon.\n"
        "Mujhe koi bhi Video bhej, aur main tujhe uska Instant Download & Watch Link bana kar dunga (Supports MX Player / VLC).\n\n"
        "Bhej koi video check karne ke liye! 🚀"
    )
    await message.reply_text(text)

@bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def bot_stats(client: Client, message: Message):
    msg = await message.reply("Fetching stats...")
    users, files = await get_stats()
    text = f"📊 **Bot Stats**\n\n👥 Total Users: `{users}`\n📂 Total Files: `{files}`"
    await msg.edit(text)

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_msg(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Kisi message ko reply karke `/broadcast` likho!")
    
    msg = await message.reply("⏳ Broadcasting...")
    users = await get_all_users()
    success, failed = 0, 0
    
    for user in users:
        try:
            await message.reply_to_message.copy(user["_id"])
            success += 1
            await asyncio.sleep(0.1) # Flood control (TG Limits bachane ke liye)
        except:
            failed += 1
            
    await msg.edit(f"✅ **Broadcast Complete!**\n\n🟢 Success: `{success}`\n🔴 Failed (Blocked bot): `{failed}`")

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def handle_files(client: Client, message: Message):
    await add_user(message.from_user.id)
    msg = await message.reply_text("⏳ Processing your file...")
    
    try:
        forwarded_msg = await message.forward(BIN_CHANNEL)
        message_id = forwarded_msg.id
        unique_id = uuid.uuid4().hex[:12]
        
        await save_file(unique_id, message_id)
        
        file = message.document or message.video or message.audio
        file_name = getattr(file, "file_name", "Video_File.mp4")
        file_size = format_size(file.file_size)
        
        safe_file_name = urllib.parse.quote(file_name)
        
        download_link = f"{WEB_URL}/dl/{safe_file_name}?id={unique_id}"
        watch_link = f"{WEB_URL}/watch/{safe_file_name}?id={unique_id}"
        
        text = (
            f"✅ ʏᴏᴜʀ ʟɪɴᴋ ɪs ʀᴇᴀᴅʏ!\n\n"
            f"📂 ғɪʟᴇ ɴᴀᴍᴇ: `{file_name}`\n"
            f"📦 ғɪʟᴇ sɪᴢᴇ: {file_size}\n\n"
            f"📥 ᴅᴏᴡɴʟᴏᴀᴅ:\n{download_link}\n\n"
            f"🖥 ᴡᴀᴛᴄʜ:\n{watch_link}\n\n"
            f"🚸 ɴᴏᴛᴇ: ʟɪɴᴋs ᴡɪʟʟ ᴡᴏʀᴋ ᴜɴᴛɪʟ ɪ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ғɪʟᴇ."
        )
        await msg.edit_text(text, disable_web_page_preview=True)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error aagaya bhai: `{e}`")

# ---- WEB SERVER: HTML PLAYER LOGIC ----
async def watch_handler(request):
    file_name = request.match_info.get("filename", "Video")
    unique_id = request.query.get("id")
    
    if not unique_id:
        return web.Response(text="❌ Invalid Link: ID is missing!", status=400)
    
    safe_file_name = urllib.parse.quote(file_name)
    stream_url = f"/dl/{safe_file_name}?id={unique_id}"
    
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
                <source src="{stream_url}" type="video/mp4">
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

# ---- WEB SERVER: FAST STREAMING LOGIC WITH SEEK SUPPORT ----
async def stream_handler(request):
    try:
        file_name = request.match_info.get("filename", "video.mp4")
        unique_id = request.query.get("id")
        
        if not unique_id:
            return web.Response(text="❌ ID missing in URL!", status=400)
            
        message_id = await get_file(unique_id)
        if not message_id:
            return web.Response(text="❌ File not found or deleted by admin!", status=404)
            
        msg = await bot.get_messages(BIN_CHANNEL, message_id)
        file = msg.document or msg.video or msg.audio
        if not file:
            return web.Response(text="❌ File format not supported!", status=404)

        file_size = file.file_size
        
        # --- MAGIC PART: HTTP RANGE SUPPORT FOR SMOOTH SEEKING ---
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
                status = 206 # Partial Content Status

        limit = end - start + 1

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(limit),
            "Content-Type": "video/mp4" if "watch" in request.path else "application/octet-stream",
            "Content-Disposition": f'inline; filename="{file_name}"' if "watch" in request.path else f'attachment; filename="{file_name}"'
        }

        response = web.StreamResponse(status=status, headers=headers)
        await response.prepare(request)

        # Telegram chunk size is 1MB (1048576 bytes)
        chunk_size = 1048576 
        offset_chunk = start // chunk_size
        skip_bytes = start % chunk_size

        try:
            async for chunk in bot.stream_media(msg, offset=offset_chunk):
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
            pass # User ne player band kar diya
            
        return response

    except Exception as e:
        print(f"Server Error: {e}")
        return web.Response(text="❌ Internal Server Error", status=500)

# ---- APP RUNNER ----
async def start_services():
    await bot.start()
    print("Bot Started Successfully!")
    
    app = web.Application()
    app.router.add_get('/watch/{filename}', watch_handler)
    app.router.add_get('/dl/{filename}', stream_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Web Server Started on Port {PORT}!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(start_services())
