from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path


class My_watchdog:
    def __init__(self, path, action, explorer):
        print("WATCHDOG")
        # Instancia del observador
        self.observer = Observer()
        self.path = Path(path)
        self.action = action
        self.explorer = explorer
        print("EXPLORER")
        print(explorer)

    def start(self):
        self.observer.schedule(
            MiHandler(self.action, self.explorer, self.path), path=self.path
        )
        self.observer.start()

        print(f"Monitoreando: {self.path} (Ctrl+C para salir)")
        try:
            while self.observer.is_alive():
                time.sleep(1)

            print("WATCHDOG STOPPED")
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        print("perrito parado")


class MiHandler(FileSystemEventHandler):
    def __init__(self, action, explorer, path):
        self.action = action
        self.explorer = explorer
        self.path = Path(path)

    def on_created(self, event):
        print(f"Archivo creado: {event.src_path}")
        self.load_new_path(self.path)

    def on_deleted(self, event):
        print(f"Archivo eliminado: {event.src_path}")
        self.load_new_path(self.path)

    def on_modified(self, event):
        print(f"Archivo modificado: {event.src_path}")
        self.load_new_path(self.path)

    def on_moved(self, event):
        print(f"Archivo movido: {event.src_path} → {event.dest_path}")
        self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        print(type(path))
        print(path)
        print(type(self.explorer))
        print(self.explorer)
        self.explorer.load_new_path(path)
