from aiohttp import web
import asyncio

async def keep_alive(request):
    return web.Response(text="Bot is alive!")

app = web.Application()
app.router.add_get("/", keep_alive)

# Run server in background
async def start_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
