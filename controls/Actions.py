from utilities.file_manager import File_manager
from pathlib import Path
import sys, shutil
from utilities.file_manager import File_manager
import gi
from gi.repository import Gtk


def on_exit(action, param):
    """
    Para salir desde el menú Archivo -> Exit.
    """
    sys.exit(0)


def entry_on_enter_change_path(entry, explorer):
    """
    Al cambiar de directorio escribiéndolo a mano en el entry
    """
    path = Path(entry.get_text())
    change_path(explorer, path)


def on_doble_click(column_view, position, explorer, entry):
    """
    Doble click en una fila de directorio y entra en él. Click en '..' y atrasamos un directorio en el path. No abre archivos actualmente
    """
    type = explorer.store[position].type
    if type == "FILE" or type == "LN BREAK":
        text = "¡Advertencia! Esta intentando abrir un archivo, esta opción aún no esta disponible."
        show_msg_alert(text)
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

    change_path(explorer, path)
    entry.set_text(str(path))


def change_path(explorer, path: Path):
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
        show_msg_alert(text)


def show_msg_alert(text_input: str):
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


def set_explorer_focused(focused_explorer, unfocused_explorer, win):
    """
    Gestión de qué explorador tiene el foco
    """
    controller = Gtk.GestureClick()

    def on_pressed(gesture, n_press, x, y):
        print(focused_explorer)
        print(unfocused_explorer)
        if win.explorer_focused:
            win.explorer_nofocused = win.explorer_focused
            selection = win.explorer_focused.get_selection()
            selection.unselect_all()

        win.explorer_nofocused = unfocused_explorer
        win.explorer_focused = focused_explorer

    controller.connect("pressed", lambda *args: on_pressed(*args))
    return controller


def on_copy(source, destination, button=None):
    """
    TODO, copiar ficheros o directorios.
    """

    if not source:
        show_msg_alert(
            "Debe seleccionar un archivo o carpeta antes de intentar copiar."
        )
        return

    selection = source.get_selection()
    selected_items = []

    for index in range(selection.get_n_items()):
        if selection.is_selected(index):
            selected_items.append(selection.get_item(index))
            print(selection.get_item(index))
    print(f"Destination: {destination.name} --> {destination.actual_path}")

    for source_item in selected_items:
        print(f"SOURCE --> {source_item.path_file}")
        print(f"DESTIONATION --> {destination.actual_path}/{source_item.name}")

        if source_item.path_file.is_dir():
            print("directorio")
            destination_str = f"{destination.actual_path}/{source_item.name}"
            shutil.copytree(
                source_item.path_file,
                destination_str,
                copy_function=shutil.copy2,
            )
        else:
            print("Archivo")
            shutil.copy2(source_item.path_file, destination.actual_path)

    destination.load_new_path(destination.actual_path)

    # HAY QUE FILTRAR EL TEMA DE COPIAR UN DIRECTORIO DENTRO DE UNO DE SUS SUBDIRECTORIOS, GENERA UN BUCLE INFINITO
    # libreria filecmp para comparar archivos y directorios
    # librería shutil para copiar


def on_create_dir():
    """
    TODO, para crear un directorio:
        - Si el directorio ya existe, que avise.
    """
    return


def on_rename():
    """
    TODO, renombrar archivos o directorios.
    Si el archivo existe:
        - Cancelar
        - Remplazar
    """
    return


def on_delete():
    """
    TODO ,para eliminar archivos y directorios.
            - pedir confirmación para borrar (eliminar, cancelar)
            - Se hará que la recursividad pida confirmación, avisando que se perderá todo. Justo después de darle a eliminar.
    """
    return


def on_move():
    """
    TODO, Mover archivos o directorios
            - Si el fichero existe, pedir confirmación sobre escribir (sobrescribir, cancelar)
    """
    return


def on_update_dir():
    """
    TODO, pulsar para actualizar directorio actual.
    """

    return
