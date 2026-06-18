# Server Monitor Bot

Telegram bot for monitoring Linux servers and Docker containers.

## Features

* CPU usage monitoring
* RAM usage monitoring
* Disk usage monitoring
* Docker container monitoring
* Xray container monitoring
* Amnezia container monitoring
* Telegram notifications
* Automatic health checks every 5 minutes

## Commands

### /status

Show current server status:

* CPU usage
* RAM usage
* Disk usage

### /docker

Show status of all Docker containers.

### /xray

Show status of Xray and Amnezia containers.

### /restartxray

Restart Xray and Amnezia containers.

## Alerts

The bot automatically sends notifications when:

* CPU usage exceeds 80%
* RAM usage exceeds 90%
* Disk usage exceeds 90%
* Xray container stops
* Amnezia container stops

## Requirements

* Python 3.10+
* Docker
* Telegram Bot Token

## Installation

```bash
git clone https://github.com/yourusername/server-monitor-bot.git
cd server-monitor-bot

pip install -r requirements.txt
```

Create environment variables:

```env
TOKEN=YOUR_BOT_TOKEN
CHAT_ID=YOUR_CHAT_ID
```

Run:

```bash
python bot.py
```

## Tech Stack

* Python
* python-telegram-bot
* Docker SDK
* psutil

## Author

Alexxx19
