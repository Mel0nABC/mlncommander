from utilities.file_manager import File_manager
from pathlib import Path
import sys
from utilities.file_manager import File_manager
import gi
from gi.repository import Gtk


# Archivo -> exit
def on_exit(action, param):
    sys.exit(0)


# Al cambiar de directorio escribiéndolo a mano en el entry
def entry_on_enter_change_path(entry, explorer):
    path = Path(entry.get_text())
    change_path(explorer, path)


# doble click en una fila de directorio y entra en él
def on_doble_click(column_view, position, explorer, entry):
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

    change_path(explorer, path)
    entry.set_text(str(path))


def change_path(explorer, path: Path):
    try:
        if not path.exists():
            raise FileNotFoundError()
        explorer.remove_actual_store()
        explorer.load_new_path(path)
    except FileNotFoundError:
        dialog = Gtk.MessageDialog(
            # transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text="¡Advertencia! El fichero o directorio de destino no existe",
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()
