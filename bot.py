import os
import time
import docker
import psutil
import asyncio
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

CPU_LIMIT = 80
RAM_LIMIT = 90
DISK_LIMIT = 90

CHECK_INTERVAL = 300

XRAY_CONTAINER = "xray-proxy"
AMNEZIA_CONTAINER = "amnezia-xray"

client = docker.from_env()

ALERTS = {
"cpu": False,
"ram": False,
"disk": False,
"xray": False,
"amnezia": False,
}

async def send_alert(app, text):
await app.bot.send_message(
chat_id=CHAT_ID,
text=text
)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage("/").percent

```
text = (
    f"🖥 Сервер\n\n"
    f"CPU: {cpu}%\n"
    f"RAM: {ram}%\n"
    f"DISK: {disk}%"
)

await update.message.reply_text(text)
```

async def docker_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
containers = client.containers.list(all=True)

```
text = "🐳 Docker контейнеры:\n\n"

for c in containers:
    text += f"{c.name}: {c.status}\n"

await update.message.reply_text(text)
```

async def xray_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = "📡 Xray / Amnezia\n\n"

```
for name in [XRAY_CONTAINER, AMNEZIA_CONTAINER]:
    try:
        container = client.containers.get(name)
        container.reload()
        text += f"{name}: {container.status}\n"
    except:
        text += f"{name}: not found\n"

await update.message.reply_text(text)
```

async def restart_xray(update: Update, context: ContextTypes.DEFAULT_TYPE):
try:
client.containers.get(XRAY_CONTAINER).restart()
client.containers.get(AMNEZIA_CONTAINER).restart()

```
    await update.message.reply_text(
        "✅ Xray и Amnezia перезапущены"
    )

except Exception as e:
    await update.message.reply_text(str(e))
```

def monitor(app):

```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

while True:

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    if cpu > CPU_LIMIT and not ALERTS["cpu"]:
        loop.run_until_complete(
            send_alert(app, f"🚨 CPU высокая нагрузка: {cpu}%")
        )
        ALERTS["cpu"] = True

    elif cpu <= CPU_LIMIT:
        ALERTS["cpu"] = False

    if ram > RAM_LIMIT and not ALERTS["ram"]:
        loop.run_until_complete(
            send_alert(app, f"🚨 RAM высокая нагрузка: {ram}%")
        )
        ALERTS["ram"] = True

    elif ram <= RAM_LIMIT:
        ALERTS["ram"] = False

    if disk > DISK_LIMIT and not ALERTS["disk"]:
        loop.run_until_complete(
            send_alert(app, f"🚨 DISK заполнен: {disk}%")
        )
        ALERTS["disk"] = True

    elif disk <= DISK_LIMIT:
        ALERTS["disk"] = False

    for name, key in [
        (XRAY_CONTAINER, "xray"),
        (AMNEZIA_CONTAINER, "amnezia")
    ]:

        try:

            container = client.containers.get(name)
            container.reload()

            if container.status != "running":

                if not ALERTS[key]:

                    loop.run_until_complete(
                        send_alert(
                            app,
                            f"❌ Контейнер {name} остановлен"
                        )
                    )

                    ALERTS[key] = True

            else:
                ALERTS[key] = False

        except:

            if not ALERTS[key]:

                loop.run_until_complete(
                    send_alert(
                        app,
                        f"❌ Контейнер {name} не найден"
                    )
                )

                ALERTS[key] = True

    time.sleep(CHECK_INTERVAL)
```

def main():

```
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("docker", docker_status))
app.add_handler(CommandHandler("xray", xray_status))
app.add_handler(CommandHandler("restartxray", restart_xray))

threading.Thread(
    target=monitor,
    args=(app,),
    daemon=True
).start()

print("Server Monitor Bot started")

app.run_polling()
```

if **name** == "**main**":
main()
