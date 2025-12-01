import psutil
import time
import threading
import json
import os

class ResourceMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self.stats = {
            "cpu_percent": [],
            "memory_percent": [],
            "disk_usage_percent": []
        }
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor_loop(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            self.stats["cpu_percent"].append(cpu)
            self.stats["memory_percent"].append(mem)
            self.stats["disk_usage_percent"].append(disk)
            
            if mem > 85.0:
                print(f"WARNING: High Memory Usage: {mem}%")
            
            time.sleep(self.interval)

    def get_summary(self):
        if not self.stats["cpu_percent"]:
            return {}
            
        return {
            "cpu_max": max(self.stats["cpu_percent"]),
            "cpu_avg": sum(self.stats["cpu_percent"]) / len(self.stats["cpu_percent"]),
            "memory_max": max(self.stats["memory_percent"]),
            "memory_avg": sum(self.stats["memory_percent"]) / len(self.stats["memory_percent"]),
            "disk_max": max(self.stats["disk_usage_percent"])
        }

    def save_report(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
