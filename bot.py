import os
import time
import docker
import psutil
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

CPU_LIMIT = 80
RAM_LIMIT = 90

XRAY_CONTAINER = "xray-proxy"
AMNEZIA_CONTAINER = "amnezia-xray"

client = docker.from_env()


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    text = (
        f"🖥 CPU: {cpu}%\n"
        f"💾 RAM: {ram}%\n"
        f"📀 Disk: {disk}%"
    )

    await update.message.reply_text(text)


async def docker_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    containers = client.containers.list(all=True)

    text = "🐳 Docker:\n\n"

    for c in containers:
        text += f"{c.name} : {c.status}\n"

    await update.message.reply_text(text)


async def xray_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    for name in [XRAY_CONTAINER, AMNEZIA_CONTAINER]:
        try:
            container = client.containers.get(name)
            text += f"{name}: {container.status}\n"
        except:
            text += f"{name}: not found\n"

    await update.message.reply_text(text)


def monitor(app):
    while True:

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        if cpu > CPU_LIMIT:
            app.bot.send_message(
                chat_id=CHAT_ID,
                text=f"⚠ CPU usage {cpu}%"
            )

        if ram > RAM_LIMIT:
            app.bot.send_message(
                chat_id=CHAT_ID,
                text=f"⚠ RAM usage {ram}%"
            )

        for name in [XRAY_CONTAINER, AMNEZIA_CONTAINER]:
            try:
                container = client.containers.get(name)

                if container.status != "running":
                    app.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🚨 Container {name} stopped"
                    )

            except:
                app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🚨 Container {name} not found"
                )

        time.sleep(300)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("docker", docker_status))
    app.add_handler(CommandHandler("xray", xray_status))

    threading.Thread(
        target=monitor,
        args=(app,),
        daemon=True
    ).start()

    app.run_polling()


if __name__ == "__main__":
    main()
