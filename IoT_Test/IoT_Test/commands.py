import psutil
import time

def getCpuLoad(time):
    return psutil.cpu_percent(interval=float(time))

