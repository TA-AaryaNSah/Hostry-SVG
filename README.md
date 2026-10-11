<div align="center">

# 🚀 File-2-Link

### Telegram File-to-Link & Streaming Bot

**Upload • Generate Links • Stream Anywhere**

[![Deploy on Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb)

</div>

---

## ✨ Features

- 📁 Telegram File-to-Link Conversion
- 🎬 Browser-Based Media Player
- ⚡ HTTP File Streaming
- 📥 Direct Download Links
- 🗄️ MongoDB Database Integration
- 🔒 Force Subscription System
- ⚙️ Telegram Admin Settings
- 📢 Multiple Force-Subscription Channels
- 🌐 HTTP Web Server
- ☁️ Deploy on Koyeb
- 🚀 Deploy on Render

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Pyrogram | Telegram Bot API |
| MongoDB | Database |
| Motor | Asynchronous database operations |
| AIOHTTP | Web server and streaming |
| AsyncIO | Asynchronous processing |

---

## 📂 Project Structure

```text
File-2-Link/
├── main.py
├── app.py
├── database.py
├── requirements.txt
├── Procfile
└── README.md
```

---

## 📋 Requirements

Before running the project, prepare:

- Python 3.10 or a compatible version.
- Telegram API credentials.
- A Telegram bot token.
- MongoDB database access.
- A Telegram storage channel, if required.
- A public URL for streaming links.

### Get Telegram Credentials

- Create a bot using [@BotFather](https://t.me/BotFather).
- Obtain your API ID and API hash from [my.telegram.org](https://my.telegram.org/).
- Create a database using [MongoDB Atlas](https://www.mongodb.com/atlas).

---

## 💻 Installation

### 1. Clone Repository

Clone your repository and navigate to the project directory.

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Configure the Application

Configure the Telegram credentials, database connection, administrator ID, storage channel, and other settings according to the source code.

### 4. Run the Bot

```bash
python main.py
```

---

## ⚙️ Configuration Variables

The following are recommended configuration names. The application must explicitly support these names for them to work.

| Variable | Description | Example |
|---|---|---|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API hash | `your_api_hash` |
| `BOT_TOKEN` | Telegram bot token | `your_bot_token` |
| `MONGO_URI` | MongoDB connection URI | `mongodb+srv://...` |
| `WEB_URL` | Public base URL | `https://your-app.example.com` |
| `ADMIN_ID` | Administrator Telegram user ID | `123456789` |
| `PORT` | HTTP server port | `8080` |

**Note:** Check `main.py` and `database.py` for the actual configuration names. These names are not guaranteed to match the current source code.

Never publish real credentials in your public repository.

---

## 🤖 Bot Commands

### 👤 User Commands

| Command | Description |
|---|---|
| `/start` | Start the bot and display the welcome message. |

### 👑 Admin Commands

| Command | Description |
|---|---|
| `/settings` | Open the administration settings panel. |
| `/setbin <channel_id>` | Configure the file-storage channel. |
| `/addfsub <channel_id> <invite_link>` | Add a force-subscription channel. |

The application has been described as supporting up to five force-subscription channels. Confirm this limit in the source code.

### Command Examples

**Set Storage Channel**

```text
/setbin -1001234567890
```

**Add Force Subscription**

```text
/addfsub -1001234567890 https://t.me/yourchannel
```

Replace the example values with your actual channel ID and invite link.

---

## 🔗 Web Endpoints

| Endpoint | Description |
|---|---|
| `/` | Basic health-check endpoint |
| `/watch/{hash}/{filename}` | Browser-based media player |
| `/{hash}/{filename}` | File streaming endpoint |

### Example Streaming URL

```text
https://your-domain.example/FILE_HASH/video.mp4
```

### Example Player URL

```text
https://your-domain.example/watch/FILE_HASH/video.mp4
```

These are example URL formats. Actual URLs depend on the running application and its configuration.

---

## ☁️ Deploy on Koyeb

<div align="center">

[![Deploy on Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy)

</div>

### Deployment Steps

1. Click the Deploy on Koyeb button.
2. Connect your GitHub account.
3. Select your repository and branch.
4. Configure the required application settings.
5. Configure the build and run commands.
6. Deploy the application.
7. Check the runtime logs.

**Run Command:**

```bash
python main.py
```

Use this command if `main.py` starts both the Telegram bot and streaming server.

Documentation: [Koyeb Deployment Guide](https://www.koyeb.com/docs/build-and-deploy/deploy-with-git)

---

## 🌐 Deploy on Render

<div align="center">

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

</div>

### Deployment Steps

1. Click the Deploy to Render button.
2. Connect your GitHub account.
3. Select your repository.
4. Configure the service and required settings.
5. Set the correct Python start command.
6. Deploy the service.
7. Inspect the runtime logs.

**Start Command:**

```bash
python main.py
```

Use this command if `main.py` starts the complete application.

Documentation: [Render Documentation](https://render.com/docs)

---

## 🔄 How It Works

1. A user starts the Telegram bot.
2. The user sends a supported file.
3. The bot checks configured subscription requirements.
4. The file is stored or forwarded according to the application configuration.
5. File metadata is stored in MongoDB.
6. A link is generated for the file.
7. The user opens the link to stream or download the file.

The exact workflow depends on the implementation and configuration.

---

## 🔧 Troubleshooting

### Bot Does Not Start

- Verify the Telegram credentials.
- Install the required dependencies.
- Check the application logs.
- Confirm the configured startup command.

### MongoDB Connection Error

- Verify the MongoDB connection URI.
- Check database permissions.
- Confirm network access from the hosting platform.

### Streaming Links Do Not Work

- Confirm that the web server is running.
- Check the configured public URL.
- Verify the file metadata.
- Check the streaming route and server logs.

### Deployment Succeeds but the Bot Is Offline

- Check the runtime logs.
- Confirm that `main.py` starts the Telegram bot.
- Verify the bot token.
- Ensure the hosting service remains running.

---

## 🔐 Security

- Never expose your Telegram bot token.
- Keep MongoDB credentials private.
- Restrict administrative commands to authorized users.
- Give the bot only the channel permissions it needs.
- Use HTTPS for public links.
- Avoid publishing private files or sensitive links.
- Share only content you are authorized to distribute.

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a branch.
3. Make your changes.
4. Test your changes.
5. Submit a pull request.

---

## 📄 License

Check the repository for an applicable license before redistributing or modifying the project.

---

<div align="center">

# ⭐ File-2-Link

**Upload • Link • Stream**

</div>
