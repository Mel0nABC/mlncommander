from pathlib import Path

from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.rename_dialog import Rename_dialog
from views.selected_for_copy import Selected_for_copy
from views.selected_for_delete import Selected_for_delete
from views.copying import Copying
import sys, shutil, filecmp
import gi, os, time, asyncio, threading, multiprocessing

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib


class Actions:

    def __init__(self):

        self.parent = None

        self.copying_dialog = None
        self.progress_on = False

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self, parent):
        return self.parent

    def on_exit(action, param):
        """
        Para salir desde el menú Archivo -> Exit.
        """
        sys.exit(0)

    def entry_on_enter_change_path(self, entry, explorer):
        """
        Al cambiar de directorio escribiéndolo a mano en el entry
        """
        path = Path(entry.get_text())
        self.change_path(explorer, path)

    def on_doble_click(self, column_view, position, explorer, entry):
        """
        Doble click en una fila de directorio y entra en él. Click en '..' y atrasamos un directorio en el path. No abre archivos actualmente
        """
        type = explorer.store[position].type
        if type == "FILE" or type == "LN BREAK":
            text = "¡Advertencia! Esta intentando abrir un archivo, esta opción aún no esta disponible."
            self.action.show_msg_alert(text)
            return

        path = explorer.store[position].path_file
        if path.name == "..":
            actual_path_str = str(explorer.actual_path)
            folders = actual_path_str.split("/")
            folders.pop()

            if len(folders) == 1:
                output_folder = "/"
            else:
                output_folder = ""

                for i in folders:
                    if not i == "":
                        output_folder += f"/{i}"

            path = Path(output_folder)

        self.change_path(explorer, path)

    def change_path(self, explorer, path: Path):
        """
        Accedemos a otro directorio.
        """
        try:
            if not path.exists():
                raise FileNotFoundError()
            explorer.remove_actual_store()
            explorer.load_new_path(path)
        except FileNotFoundError:
            text = "¡Advertencia! El fichero o directorio de destino no existe"
            self.action.show_msg_alert(text)

    def show_msg_alert(self, text_input: str):
        """
        Mensaje de alerta genérico, se le pasa el texto deseado
        """
        dialog = Gtk.MessageDialog(
            # transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text=text_input,
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

    @staticmethod
    def set_explorer_src(focused_explorer, unfocused_explorer, win):
        """
        Gestión de qué explorador tiene el foco
        """
        controller = Gtk.GestureClick()

        def on_pressed(gesture, n_press, x, y):
            if win.explorer_src:
                win.explorer_dst = win.explorer_src
                selection = win.explorer_src.get_selection()
                selection.unselect_all()

            win.explorer_dst = unfocused_explorer
            win.explorer_src = focused_explorer

        controller.connect("pressed", lambda *args: on_pressed(*args))
        return controller

