from pathlib import Path

from views.overwrite_options import Overwrite_dialog
from views.rename_dialog import Rename_dialog
from views.selected_for_delete import Selected_for_delete
from views.copying import Copying
import gi, sys

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib


class Actions:

    def __init__(self):

        self.parent = None

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
            self.show_msg_alert(self.parent, text)
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
            explorer.load_new_path(path,0)
            explorer.update_watchdog_path(path, explorer)
        except FileNotFoundError:
            text = "¡Advertencia! El fichero o directorio de destino no existe"
            self.show_msg_alert(text)

    def show_msg_alert(self, parent, text_input: str):
        """
        Mensaje de alerta genérico, se le pasa el texto deseado
        """
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text=text_input,
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()

    @staticmethod
    def set_explorer_src(explorer_focused, win):
        """
        Gestión de qué explorador tiene el foco
        """
        explorer_left = win.explorer_1
        explorer_right = win.explorer_2

        if explorer_focused == explorer_left:
            explorer_left.focused = True
            explorer_right.focused = False
            explorer_right.selection.unselect_all()
            win.set_explorers_types(explorer_left, explorer_right)

        else:
            explorer_right.focused = True
            explorer_left.focused = False
            explorer_left.selection.unselect_all()
            win.set_explorers_types(explorer_right, explorer_left)

    def get_selected_items_from_explorer(self, explorer):
        """
        Obtiene la lista de selection de un explorer
        """
        selection = explorer.get_selection()
        selected_items = []
        for index in range(selection.get_n_items()):
            if selection.is_selected(index):
                item = selection.get_item(index).path_file
                if not str(item) == "..":
                    selected_items.append(selection.get_item(index).path_file)

        return selected_items
