from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time, gi
from gi.repository import GLib
from pathlib import Path
from utilities.file_manager import File_manager


class My_watchdog:
    def __init__(self, path, explorer):
        self.observer = Observer()
        self.path = Path(path)
        self.explorer = explorer

    def start(self):
        self.observer.schedule(
            MiHandler(self.path, self.explorer), path=self.path, recursive=False
        )
        self.observer.start()

        try:
            while self.observer.is_alive():
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class MiHandler(FileSystemEventHandler):
    def __init__(self, path, explorer):
        self.explorer = explorer
        self.path = Path(path)

    def on_created(self, event):
        # print(f"Archivo creado: {event.src_path}")
        self.load_new_path(self.path)

    def on_deleted(self, event):
        # print(f"Archivo eliminado: {event.src_path}")
        self.load_new_path(self.path)

    def on_modified(self, event):
        # print(f"Archivo modificado: {event.src_path}")
        self.load_new_path(self.path)

    def on_moved(self, event):
        # print(f"Archivo movido: {event.src_path} → {event.dest_path}")
        self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        # if path.exists():
        # GLib.idle_add(self.explorer.load_new_data_path, path)
