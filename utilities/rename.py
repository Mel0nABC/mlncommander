from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


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
    response = await rename_dialog.wait_response_async()
    return response
