import os
import math
import uuid
import asyncio
import urllib.parse
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message
from database import save_file, get_file

# --- TERE HARDCODED CREDENTIALS ---
API_ID = 32541562
API_HASH = "e37e4432298d5a5eb4a6e32c18804283"
BOT_TOKEN = "8932447404:AAGZ1I0ZLesk3DIZw-IVCtliPLd4O9HVFAA"
BIN_CHANNEL = -1002521835919

# Yeh tujhe Render pe dalna padega, ya URL milne ke baad yahan hardcode kar dena
WEB_URL = os.environ.get("WEB_URL", "https://your-app-name.onrender.com") 
PORT = int(os.environ.get("PORT", 8080))

bot = Client("StreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def format_size(bytes_size):
    if bytes_size >= 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
    return f"{bytes_size / (1024 * 1024):.2f} MB"

# ---- TELEGRAM BOT LOGIC ----

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def handle_files(client: Client, message: Message):
    msg = await message.reply_text("⏳ Processing...")
    
    try:
        # File forward aur DB save
        forwarded_msg = await message.forward(BIN_CHANNEL)
        message_id = forwarded_msg.id
        unique_id = uuid.uuid4().hex[:12]
        await save_file(unique_id, message_id)
        
        file = message.document or message.video or message.audio
        file_name = getattr(file, "file_name", "Video.mp4")
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
        await msg.edit_text(f"❌ Error: {e}")

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
            body {{
                margin: 0; padding: 0; background-color: #0f0f0f;
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                height: 100vh; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .player-container {{
                width: 90%; max-width: 850px; background: #1a1a1a;
                padding: 15px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.6);
            }}
            h3 {{ margin-top: 0; font-size: 16px; word-wrap: break-word; color: #ccc; text-align: center; }}
            video {{ width: 100%; border-radius: 8px; outline: none; background: #000; }}
            .download-btn {{
                display: block; width: max-content; margin: 15px auto 0;
                padding: 10px 20px; background: #0088cc; color: white;
                text-decoration: none; border-radius: 6px; font-weight: bold; transition: 0.3s;
            }}
            .download-btn:hover {{ background: #006699; }}
        </style>
    </head>
    <body>
        <div class="player-container">
            <h3>{file_name}</h3>
            <video controls controlsList="nodownload">
                <source src="{stream_url}" type="video/mp4">
                Your browser does not support HTML video.
            </video>
            <a href="{stream_url}" class="download-btn" download>⬇️ Download File</a>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")

# ---- WEB SERVER: STREAMING / DOWNLOAD LOGIC ----

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
        
        headers = {
            "Content-Type": "application/octet-stream" if "dl" in request.path else "video/mp4",
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        }

        response = web.StreamResponse(status=200, headers=headers)
        response.content_length = file_size
        await response.prepare(request)

        async for chunk in bot.stream_media(msg):
            await response.write(chunk)
            
        return response

    except Exception as e:
        print(f"Server Error: {e}")
        return web.Response(text="❌ Internal Server Error", status=500)

# ---- APP RUNNER ----

async def start_services():
    await bot.start()
    print("Bot Started!")
    
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
    asyncio.run(start_services())
