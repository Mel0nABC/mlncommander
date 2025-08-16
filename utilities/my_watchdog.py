from utilities.i18n import _
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import gi  # noqa: F401

from gi.repository import GLib


class My_watchdog:
    def __init__(
        self,
        path: Path,
        APP_USER_PATH: Path,
        explorer: "Explorer" = None,  # noqa: F821
    ) -> None:
        self.observer = Observer()
        self.path = Path(path)
        self.APP_USER_PATH = APP_USER_PATH
        self.explorer = explorer

    def start(self):
        """
        Initialize watchdog
        """
        self.observer.schedule(
            MiHandler(self.path, self.explorer, self.APP_USER_PATH),
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

    def __init__(
        self,
        path: Path,
        explorer: "Explorer",  # noqa: F821
        APP_USER_PATH: Path,
    ):

        self.explorer = explorer
        self.path = Path(path)
        self.log_file = Path(f"{APP_USER_PATH}/log/mlncommander.log")
        self.date_str = time.strftime("%A, %d/%m/%Y - %H:%M:%S")

        try:

            if not self.log_file.parent.exists():
                self.log_file.parent.mkdir()

            if not self.log_file.exists():

                self.log_file.write_text(
                    _(
                        "##################################################\n"
                        "########## INICIALIZANDO ARCHIVO  DE LOG #########\n"
                        "##################################################\n"
                        f"######## {self.date_str}  ########\n"
                        "##################################################\n"
                    )
                )
        except Exception as e:
            print(f"ERROR: {e}")

    # def dispatch(self, event):
    #     print(event)
    #     self.last_event = event

    def on_created(self, event) -> None:
        self.print_status_on_log(_("CREADO"), event.src_path)
        self.load_new_path(self.path)

    def on_deleted(self, event) -> None:
        self.print_status_on_log(_("BORRADO"), event.src_path)
        self.load_new_path(self.path)

    # def on_modified(self, event) -> None:
    #     self.print_status_on_log(_("MODIFICADO"), event.src_path)
    #     self.load_new_path(self.path)

    # def on_moved(self, event) -> None:
    #     self.print_status_on_log(_("MOVIDO"), event.src_path)
    #     self.load_new_path(self.path)

    def load_new_path(self, path):
        path = Path(path)
        if path.exists():
            GLib.idle_add(self.explorer.load_data, path)

    def print_status_on_log(self, operation: str, src_path: Path) -> None:
        try:
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(_(f"{operation}: {self.date_str} -- {src_path} \n"))
        except Exception as e:
            text = _("Algún problema ha ocurrido")
            print(f"{text}: {e}")
