from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import gi

gi.require_version("Gtk", "4.0")


class My_watchdog:
    def __init__(self, path, explorer):
        self.observer = Observer()
        self.path = Path(path)
        self.explorer = explorer

    def start(self):
        """
        Initialize watchdog
        """
        self.observer.schedule(
            MiHandler(self.path, self.explorer),
            path=self.path,
            recursive=False,
        )
        self.observer.start()

        try:
            while self.observer.is_alive():
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """
        Stop watchdog
        """
        self.observer.stop()
        self.observer.join()


class MiHandler(FileSystemEventHandler):
    """
    Control diferent events handler
    """

    def __init__(self, path, explorer):
        self.explorer = explorer
        self.path = Path(path)

    def on_created(self, event) -> None:
        # print(f"Archivo creado: {event.src_path}")
        self.load_new_path(self.path)

    def on_deleted(self, event) -> None:
        # print(f"Archivo eliminado: {event.src_path}")
        self.load_new_path(self.path)

    def on_modified(self, event) -> None:
        # print(f"Archivo modificado: {event.src_path}")
        self.load_new_path(self.path)

    def on_moved(self, event) -> None:
        # print(f"Archivo movido: {event.src_path} → {event.dest_path}")
        self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        # if path.exists():
        #     print("WATCHDOG")
        # GLib.idle_add(self.explorer.load_data, path)
