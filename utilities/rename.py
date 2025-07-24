from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.rename_dialog import Rename_dialog
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Rename_Logic:

    def __init__(self, event=None):
        print("Dialog Rename")
        self.response = None
        self.event = event

    def on_rename(self, explorer_src, explorer_dst):
        """
        TODO, renombrar archivos o directorios.
        Si el archivo existe:
            - Cancelar
            - Remplazar
        """

        return

    async def create_dialog_rename(self, parent, dst_info):
        rename_dialog = Rename_dialog(parent, dst_info)
        self.response = await rename_dialog.wait_response_async()

    def get_response(self):
        return self.response
