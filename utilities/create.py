from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.create_dir_dialog import Create_dir_dialog
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Create:

    def __init__(self):
        self.action = Actions()

    def on_create_dir(self, explorer_dst, parent, button=None):
        """
        TODO, para crear un directorio:
            - Si el directorio ya existe, que avise.
        """

        if not explorer_dst:
            self.action.show_msg_alert("Debe seleccionar explorador.")
            return

        asyncio.ensure_future(self.on_create_dir_async(explorer_dst, parent))

    async def on_create_dir_async(self, explorer_dst, parent):
        create_dir = Create_dir_dialog(parent, explorer_dst)
        response = await create_dir.wait_response_async()
        dst_dir = Path(f"{explorer_dst.actual_path}/{response}")

        if explorer_dst.actual_path == dst_dir or not response.strip():
            self.action.show_msg_alert("Debes introducir algún nombre válido.")
            return

        if dst_dir.exists():
            self.action.show_msg_alert("El directorio que quiere crear, ya existe.")
            return

        if dst_dir.name == "None":
            return

        os.mkdir(dst_dir)
        self.action.change_path(explorer_dst, explorer_dst.actual_path)
