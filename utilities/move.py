from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


def on_move(self, explorer_src, explorer_dst):
    """
    TODO, Mover archivos o directorios
            - Si el fichero existe, pedir confirmación sobre escribir (sobrescribir, cancelar)
    """
    selected_items = selected_items = self.get_selected_items_from_explorer(
        explorer_src
    )
    for i in selected_items:
        print(i)
    return
