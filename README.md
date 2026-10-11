<div align="center">🚀 Hostry-SVG

Telegram File-to-Link & Streaming Bot

Upload Files • Generate Links • Stream Anywhere

""Deploy on Koyeb" (https://www.koyeb.com/static/images/deploy/button.svg)" (https://app.koyeb.com/deploy?name=Hostry-SVG&type=git&repository=TA-AaryaNSah%2FHostry-SVG&branch=main)

""Deploy to Render" (https://render.com/images/deploy-to-render-button.svg)" (https://render.com/deploy?repo=https://github.com/TA-AaryaNSah/Hostry-SVG)

""Python" (https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)" (https://www.python.org/)
""Telegram Bot" (https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram)" (https://telegram.org/)
""MongoDB" (https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb)" (https://www.mongodb.com/)

</div>---

✨ Features

- 📁 Telegram file-to-link conversion
- 🎬 Browser-based media player
- ⚡ HTTP streaming support
- 📥 File download links
- 🗄️ MongoDB database integration
- 🔒 Force-subscription functionality
- ⚙️ Telegram admin settings
- 📢 Support for multiple subscription channels
- ☁️ Deployment support for Koyeb and Render

---

🧩 Configuration Reference

Configure the values required by the application before running it.

Variable| Description
"API_ID"| Telegram API ID
"API_HASH"| Telegram API hash
"BOT_TOKEN"| Telegram bot token
"MONGO_URI"| MongoDB connection string
"WEB_URL"| Public URL used for generated links
"ADMIN_ID"| Telegram administrator user ID
"PORT"| HTTP server port

Note: These are recommended configuration names. The current code must read the corresponding variables for them to work. Check "main.py" and "database.py" for the actual configuration names.

---

☁️ Deployment

Deploy on Koyeb

1. Click Deploy on Koyeb above.
2. Connect your GitHub account if requested.
3. Select the repository and branch.
4. Configure the application's required credentials.
5. Confirm the build and start commands.
6. Deploy and inspect the runtime logs.

Deploy on Render

1. Click Deploy to Render above.
2. Connect your GitHub account.
3. Configure the service and required credentials.
4. Set the correct Python start command.
5. Deploy and verify that the bot and streaming server start successfully.

Important: The deployment buttons open the respective deployment workflows. They do not automatically configure credentials or guarantee a successful deployment.

---

🤖 Bot Commands

Command| Description
"/start"| Start the bot
"/settings"| Open the admin settings
"/setbin <channel_id>"| Configure the storage channel
"/addfsub <channel_id> <invite_link>"| Add a subscription channel

---

🔗 Web Endpoints

Endpoint| Description
"/"| Health check
"/watch/{hash}/{filename}"| Web player
"/{hash}/{filename}"| File streaming

---

🔐 Security

- Never publish your bot token or database credentials.
- Restrict administrative commands to authorized users.
- Use HTTPS for public streaming links.
- Share only files you have permission to distribute.

---

<div align="center">Hostry-SVG — Upload • Link • Stream

</div>
