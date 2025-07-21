from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Move:
    def __init__(self):
        self.action = Actions()

    def on_move(self, explorer_src, explorer_dst):
        """
        TODO, Mover archivos o directorios
                - Si el fichero existe, pedir confirmación sobre escribir (sobrescribir, cancelar)
        """
        selected_items = selected_items = self.action.get_selected_items_from_explorer(
            explorer_src
        )
        dst_dir = explorer_dst.actual_path
        for item in selected_items:
            src_info = item
            parent = item.parent

            if str(parent) == str(dst_dir):
                self.action.show_msg_alert(
                    "Estás queriendo mover el contenido al mismo directorio"
                )
                return
            dst_dir_new_folder = f"{src_info}"
            if src_info == dst_dir:
                self.action.show_msg_alert(
                    "Estas intentando mover un directorio dentro de sí mismo"
                )
                continue

            print(src_info)

            # HAY QUE ACTIVAR OVERWRITE DIALOG POR SI EXISTE EN DESTINO
            # RECORRER TODOS LOS SUBDIRECTORIOS, shutil.move DETECTA SI EXISTE Y LANZA EXCEPCIÓN
