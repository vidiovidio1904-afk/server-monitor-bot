import psutil

print("CPU:", psutil.cpu_percent())
print("RAM:", psutil.virtual_memory().percent)
print("DISK:", psutil.disk_usage('/').percent)
