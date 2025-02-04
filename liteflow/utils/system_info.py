import os
import psutil

def get_system_info():
    # CPU information
    cpu_count = psutil.cpu_count(logical=True)
    cpu_model = None
    with open("/proc/cpuinfo", "r") as f:
        info = f.readlines()
    for line in info:
        if "model name" in line:
            cpu_model = line.split(":")[1].strip()
            break

    # Memory information
    ram = psutil.virtual_memory().total / (1024 ** 3)  # GB

    # Disk usage for home directory
    home_directory = os.path.expanduser("~")  # Gets the home directory path
    disk_usage = psutil.disk_usage(home_directory)
    disk_used = disk_usage.used / (1024 ** 3)  # GB
    disk_total = disk_usage.total / (1024 ** 3)  # GB
    disk_free = disk_usage.free / (1024 ** 3)  # GB

    # OS information
    os_info = {}
    with open("/etc/os-release", "r") as f:
        for line in f:
            if "NAME" in line or "VERSION_ID" in line:
                key, value = line.strip().split("=")
                os_info[key] = value.strip('"')

    return {
        "cpu_count": cpu_count,
        "cpu_model": cpu_model,
        "ram_total": round(ram, 2),
        "disk_used": round(disk_used, 2),
        "disk_total": round(disk_total, 2),
        "disk_free": round(disk_free, 2),
        "os_name": os_info.get("NAME", "N/A"),
        "os_version": os_info.get("VERSION_ID", "N/A")
    }
