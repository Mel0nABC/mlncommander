from utilities.file_manager import File_manager
from entity.File_or_directory_info import File_or_directory_info
from pathlib import Path
from datetime import datetime
from utilities.file_manager import File_manager
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy

import sys, shutil, filecmp
import gi, os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Actions:

    def __init__(self, parent):

        self.source_file_general = None
        self.destination_file_general = None
        self.parent = parent

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
            self.show_msg_alert(text)
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
        entry.set_text(str(path))

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
            self.show_msg_alert(text)

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
    def set_explorer_focused(focused_explorer, unfocused_explorer, win):
        """
        Gestión de qué explorador tiene el foco
        """
        controller = Gtk.GestureClick()

        def on_pressed(gesture, n_press, x, y):
            if win.explorer_focused:
                win.explorer_nofocused = win.explorer_focused
                selection = win.explorer_focused.get_selection()
                selection.unselect_all()

            win.explorer_nofocused = unfocused_explorer
            win.explorer_focused = focused_explorer

        controller.connect("pressed", lambda *args: on_pressed(*args))
        return controller

    def on_copy(self, explorer_src, explorer_dst, parent, button=None):
        """
        TODO, copiar ficheros o directorios.
        """

        if not explorer_src:
            self.show_msg_alert(
                "Debe seleccionar un archivo o carpeta antes de intentar copiar."
            )
            return

        selection = explorer_src.get_selection()
        self.selected_items = []
        for index in range(selection.get_n_items()):
            if selection.is_selected(index):
                self.selected_items.append(selection.get_item(index))

        if explorer_src.actual_path == explorer_dst.actual_path:
            self.show_msg_alert("Intentar copiar un archivo a él mismo")
            return

        copy_window = Selected_for_copy(
            self.parent, self, explorer_src, explorer_dst, self.selected_items
        )

    def copy_one_file_dir(self, explorer_src, explorer_dst, parent, selected_items):
        print("COPIANDO UN ARCHIVO")
        source_file = selected_items[0].path_file
        destination_file = Path(f"{explorer_dst.actual_path}/{source_file.name}")

        if not destination_file.exists():
            # NO EXISTE
            if source_file.is_dir():
                # ES UN DIRECTORIO
                # Comprobar si el directorio destino es dos veces el mismo que origen, para evitar copia infinita y cuelgue de la alpicación
                check_subdir_loop = str(f"{source_file}/{source_file.name}") == str(
                    f"{explorer_dst.actual_path}"
                )

                if check_subdir_loop:
                    self.show_msg_alert(
                        "Esta copiando el directorio origen en uno de sus subdirectorios, esto traerá problemas de copias infinitas"
                    )
                    return
                shutil.copytree(source_file, destination_file)
            else:
                # ES UN ARCHIVO
                shutil.copy(source_file, destination_file)
        else:
            # EXISTE
            exist_files_or_dir_one_file = []
            exist_files_or_dir_one_file.append(source_file)
            self.open_overwrite_dialog(
                parent, explorer_src, explorer_dst, exist_files_or_dir_one_file
            )

    def copy_multi_file_dir(self, parent, explorer_src, explorer_dst):
        exist_files_or_dir = []
        # MULTIPLES ARCHIVOS
        for src_item in self.selected_items:
            destination_dir = Path(f"{explorer_dst.actual_path}")
            destination_file = Path(f"{explorer_dst.actual_path}/{src_item.name}")
            # NO EXISTE
            if not destination_file.exists():
                if src_item.path_file.is_dir():
                    # ES UN DIRECTORIO
                    # Comprobar si el directorio destino es dos veces el mismo que origen, para evitar copia infinita y cuelgue de la alpicación
                    check_subdir_loop = str(f"{src_item}/{src_item.name}") == str(
                        f"{explorer_dst.actual_path}"
                    )

                    if check_subdir_loop:
                        self.show_msg_alert(
                            "Esta copiando el directorio origen en uno de sus subdirectorios, esto traerá problemas de copias infinitas"
                        )
                        return
                    shutil.copytree(str(src_item.path), str(destination_file))
                else:
                    # ES UN ARCHIVO
                    shutil.copy(str(src_item.path), str(destination_dir))

            else:
                # EXISTE

                exist_files_or_dir.append(src_item.path_file)

        self.open_overwrite_dialog(
            parent, explorer_src, explorer_dst, exist_files_or_dir
        )

    def open_overwrite_dialog(
        self, parent, explorer_src, explorer_dst, exist_files_or_dir
    ):
        print("OPEN OVERWRITE")
        if not explorer_src:
            return

        if not explorer_dst:
            return

        if not exist_files_or_dir:
            return

        def next_dialog(index):
            if index >= len(exist_files_or_dir):
                return

            src_info = exist_files_or_dir[index]
            dst_info = Path(f"{explorer_dst.actual_path}/{src_info.name}")
            overwrite_dialog = Overwrite_dialog(parent, src_info, dst_info)
            overwrite_dialog.present()

            def on_response(
                dialog,
                response_id,
                explorer_src=explorer_src,
                explorer_dst=explorer_dst,
                exist_files_or_dir=exist_files_or_dir,
            ):

                try:
                    response_general = dialog.response.get("response")
                    check_button_all_files = dialog.response.get("all_files")
                except AttributeError as e:
                    return

                if response_general == "cancel":
                    print("Cancelado")
                    return

                if response_general == "skip":
                    print("SKIP")
                    if check_button_all_files:
                        return

                    next_dialog(index + 1)
                    return

                if response_general == "overwrite":
                    if check_button_all_files:
                        for i in range(index, len(exist_files_or_dir)):
                            src = exist_files_or_dir[i]
                            self.overwrite(src, explorer_dst)
                        return

                    src = exist_files_or_dir[index]
                    self.overwrite(src, explorer_dst)

                if response_general == "overwrite_date":
                    print(response_general)

                if response_general == "overwrite_diff":
                    print(response_general)

                if response_general == "rename":
                    print(response_general)

                next_dialog(index + 1)

            overwrite_dialog.connect("response", on_response)

        next_dialog(0)

    def overwrite(self, src, explorer_dst):
        dst_dir = explorer_dst.actual_path
        dst = f"{dst_dir}/{src.name}"
        update_path = Path(dst_dir)
        old_name = f"{dst}.old"
        os.rename(dst, old_name)
        old_file = Path(old_name)
        if old_file.exists():
            if src.is_dir():
                shutil.copytree(src, dst)
                shutil.rmtree(old_name)
            else:
                shutil.copy(src, dst)
                os.remove(old_name)

        self.change_path(explorer_dst, update_path)

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
