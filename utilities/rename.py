from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.rename_dialog import Rename_dialog
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Rename_Logic:

    def __init__(self):
        self.response = None
        self.action = Actions()

    def on_rename(self, explorer_src, parent):
        """
        Renombrar archivos o directorios.
        """

        if not explorer_src:
            self.action.show_msg_alert(
                "Debe seleccionar un archivo o carpeta antes de intentar copiar."
            )
            return

        selected_items = self.action.get_selected_items_from_explorer(explorer_src)

        if not selected_items:
            self.action.show_msg_alert(
                "Debe seleccionar un archivo o carpeta antes de intentar copiar."
            )
            return

        self.iterator_thread = threading.Thread(
            target=self.iterator_items, args=(parent, selected_items)
        )
        self.iterator_thread.start()

    def iterator_items(self, parent, selected_items):
        for src_info in selected_items:
            self.wait_event = threading.Event()

            def run_dialog(parent, src_info):
                asyncio.ensure_future(self.create_dialog_response(parent, src_info))

            GLib.idle_add(run_dialog, parent, src_info)
            self.wait_event.wait()

            if self.response == None:
                continue

            if not self.response == src_info.name:
                new_path = Path(f"{src_info.parent}/{self.response}")
                if new_path.exists():
                    GLib.idle_add(
                        self.action.show_msg_alert,
                        f"El archivo con nombre {new_path.name}, ya existe.",
                    )
                    continue
                os.rename(src_info, new_path)

    async def create_dialog_response(self, parent, src_info):
        self.response = await self.create_dialog_rename(parent, src_info)
        self.wait_event.set()

    async def create_dialog_rename(self, parent, src_info):
        rename_dialog = Rename_dialog(parent, str(src_info))
        return await rename_dialog.wait_response_async()

    def get_response(self):
        return self.response
