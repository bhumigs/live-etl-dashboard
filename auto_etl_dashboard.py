import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from run_etl import run_etl
import subprocess

# Paths
RAW_FOLDER = "data"
CLEANED_FOLDER = "data/cleaned"
os.makedirs(CLEANED_FOLDER, exist_ok=True)

# Event handler
class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".csv"):
            filename = os.path.basename(event.src_path)
            input_file = event.src_path
            output_file = os.path.join(CLEANED_FOLDER, f"cleaned_{filename}")
            print(f"\nNew CSV detected: {filename}")
            print("Running ETL pipeline...")
            run_etl(input_file, output_file)
            print("ETL finished!")

# Start folder observer
observer = Observer()
event_handler = Watcher()
observer.schedule(event_handler, path=RAW_FOLDER, recursive=False)
observer.start()
print(f"Watching folder '{RAW_FOLDER}' for new CSV files...")

# Launch Streamlit dashboard
subprocess.Popen(["streamlit", "run", "dashboard.py"])

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
