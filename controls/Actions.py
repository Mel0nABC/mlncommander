from pathlib import Path

from views.overwrite_options import Overwrite_dialog
from views.rename_dialog import Rename_dialog
from views.selected_for_delete import Selected_for_delete
from views.copying import Copying
import gi, sys, subprocess

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

        file_or_directory = explorer.store[position]
        path = file_or_directory.path_file
        type_str = file_or_directory.type

        if type_str == "FILE" or type_str == "LN BREAK":
            try:
                subprocess.run(["xdg-open", path])
            except Exception as e:
                self.show_msg_alert(
                    self.parent,
                    f"Ha ocurrido algun problema al intentar ejecutar el archivo:\n{path}",
                )
            return

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
            explorer.load_new_path(path)
            explorer.update_watchdog_path(path, explorer)
        except FileNotFoundError:
            text = "¡Advertencia! El fichero o directorio de destino no existe"
            GLib.idle_add(self.show_msg_alert, self.parent, text)

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
    def set_explorer_to_focused(explorer_to_focused, win):
        """
        Gestión de qué explorador tiene el foco
        """
        explorer_left = win.explorer_1
        explorer_right = win.explorer_2

        try:
            if explorer_to_focused == explorer_left:
                explorer_left.focused = True
                explorer_right.focused = False
                explorer_right.selection.unselect_all()
                win.set_explorer_focused(explorer_left, explorer_right)

            else:
                explorer_right.focused = True
                explorer_left.focused = False
                explorer_left.selection.unselect_all()
                win.set_explorer_focused(explorer_right, explorer_left)
        except AttributeError as e:
            print(f"Error inicialización: {e}")
