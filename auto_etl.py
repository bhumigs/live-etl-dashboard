import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from run_etl import run_etl  # Import your ETL function

RAW_FILE = "data/worldometer_data.csv"


class ETLHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("worldometer_data.csv"):
            print(f"Detected change in {RAW_FILE}. Running ETL...")
            run_etl()  # This should run the full ETL pipeline


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    event_handler = ETLHandler()
    observer = Observer()
    observer.schedule(event_handler, path="data", recursive=False)
    observer.start()
    print("Watching for changes in worldometer_data.csv...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
