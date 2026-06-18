
import asyncio
import psutil
import docker

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import *

docker_client = docker.from_env()

alerts = {
    "cpu": False,
    "ram": False,
    "disk": False,
    "xray": False,
    "amnezia": False
}


def get_status_text():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    return (
        f"🖥 CPU: {cpu}%\n"
        f"🧠 RAM: {ram}%\n"
        f"💾 Disk: {disk}%"
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_status_text())


async def docker_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    containers = docker_client.containers.list(all=True)

    msg = "🐳 Docker Containers\n\n"

    for c in containers:
        msg += f"{c.name}: {c.status}\n"

    await update.message.reply_text(msg)


async def xray_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ""

    for name in [XRAY_CONTAINER, AMNEZIA_CONTAINER]:
        try:
            c = docker_client.containers.get(name)
            msg += f"{name}: {c.status}\n"
        except:
            msg += f"{name}: NOT FOUND\n"

    await update.message.reply_text(msg)


async def monitor_loop(app):
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        if cpu > CPU_LIMIT and not alerts["cpu"]:
            alerts["cpu"] = True
            await app.bot.send_message(
                CHAT_ID,
                f"🚨 CPU HIGH: {cpu}%"
            )

        if cpu <= CPU_LIMIT:
            alerts["cpu"] = False

        if ram > RAM_LIMIT and not alerts["ram"]:
            alerts["ram"] = True
            await app.bot.send_message(
                CHAT_ID,
                f"🚨 RAM HIGH: {ram}%"
            )

        if ram <= RAM_LIMIT:
            alerts["ram"] = False

        if disk > DISK_LIMIT and not alerts["disk"]:
            alerts["disk"] = True
            await app.bot.send_message(
                CHAT_ID,
                f"🚨 DISK HIGH: {disk}%"
            )

        if disk <= DISK_LIMIT:
            alerts["disk"] = False

        for key, container_name in [
            ("xray", XRAY_CONTAINER),
            ("amnezia", AMNEZIA_CONTAINER)
        ]:
            try:
                container = docker_client.containers.get(container_name)

                if container.status != "running":
                    if not alerts[key]:
                        alerts[key] = True

                        await app.bot.send_message(
                            CHAT_ID,
                            f"🚨 Container stopped: {container_name}"
                        )
                else:
                    alerts[key] = False

            except Exception:
                if not alerts[key]:
                    alerts[key] = True

                    await app.bot.send_message(
                        CHAT_ID,
                        f"🚨 Container missing: {container_name}"
                    )

        await asyncio.sleep(CHECK_INTERVAL)


async def on_startup(app):
    asyncio.create_task(monitor_loop(app))


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("docker", docker_cmd))
    app.add_handler(CommandHandler("xray", xray_cmd))

    app.post_init = on_startup

    print("Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
