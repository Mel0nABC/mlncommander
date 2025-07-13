from utilities.file_manager import File_manager
from pathlib import Path
from datetime import datetime
from utilities.file_manager import File_manager
from views.overwrite_options import Overwrite_dialog
import sys, shutil, filecmp
import gi, os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class Actions:

    def __init__(self):

        self.source_file_general = None
        self.destination_file_general = None

        self.check_button_all_files = None
        self.response_general = None

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
        self.destination_file = explorer_dst.actual_path
        for index in range(selection.get_n_items()):
            if selection.is_selected(index):
                self.selected_items.append(selection.get_item(index))

        # Cuando sólo se copia un archivo o un directorio
        if len(self.selected_items) == 1:
            self.copy_one_file_dir(explorer_src, explorer_dst, parent)
        else:
            # Cuando se copian varios arcivos o directorios
            self.copy_multi_file_dir(explorer_src, explorer_dst, parent)

        explorer_dst.load_new_path(explorer_dst.actual_path)

    def copy_one_file_dir(self, explorer_src, explorer_dst, parent):
        source_file = self.selected_items[0].path_file
        self.destination_file = Path(f"{explorer_dst.actual_path}/{source_file.name}")
        if not self.destination_file.exists():
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
                shutil.copytree(source_file, self.destination_file)
            else:
                # ES UN ARCHIVO
                shutil.copy(source_file, self.destination_file)
        else:
            # EXISTE
            print("EXISTE")
            self.filter_exist_file_or_dir(parent, explorer_dst, self.selected_items)

    def copy_multi_file_dir(self, explorer_src, explorer_dst, parent):
        self.exist_files_or_dir = []
        # MULTIPLES ARCHIVOS
        for item in self.selected_items:
            destination_dir = Path(f"{explorer_dst.actual_path}")
            destination_file = Path(f"{explorer_dst.actual_path}/{item.name}")
            # NO EXISTE
            if not destination_file.exists():
                if item.path_file.is_dir():
                    # ES UN DIRECTORIO
                    # Comprobar si el directorio destino es dos veces el mismo que origen, para evitar copia infinita y cuelgue de la alpicación
                    check_subdir_loop = str(f"{item}/{item.name}") == str(
                        f"{explorer_dst.actual_path}"
                    )

                    if check_subdir_loop:
                        self.show_msg_alert(
                            "Esta copiando el directorio origen en uno de sus subdirectorios, esto traerá problemas de copias infinitas"
                        )
                        return
                    shutil.copytree(str(item.path), str(destination_file))
                else:
                    # ES UN ARCHIVO
                    shutil.copy(str(item.path), str(destination_dir))

            else:
                # EXISTE
                self.exist_files_or_dir.append(item)

        # SI HAY ALGÚN ARCHIVO REPETIDO
        if self.exist_files_or_dir:
            self.filter_exist_file_or_dir(parent, explorer_dst, self.exist_files_or_dir)

    def filter_exist_file_or_dir(self, parent, explorer_dst, exist_files_or_dir):
        print("LISTA DE ARCHIVOS QUE EXISTEN EN DST")
        for i in exist_files_or_dir:
            destination = i.path_file

            # COMPROBAR SI HAY CONTENIDO EN LA RUTA DESTINO (SÓLO DIRECTORIOS), SALTA AL SIGUIENTE ELEMENTO SI ESTÁ  VACÍO
            if destination.is_dir():
                try:
                    next(destination.iterdir())
                except:
                    continue

            
            
            
            

    def open_overwrite_dialog(self, parent, explorer_dst, exist_files_or_dir):
        print("OPEN OVERWRITE")

        def on_response(
            dialog,
            response_id,
            explorer_dst=explorer_dst,
            exist_files_or_dir=exist_files_or_dir,
        ):

            for item in exist_files_or_dir:
                print(f"EXISTE -> {item}")
                # source = item.path_file
                # self.response_general = dialog.response.get("response")
                # self.check_button_all_files = dialog.response.get("all_files")

                # destination_dir = explorer_dst.actual_path

                # if destination_dir.is_dir():
                #     destination_dir = Path(f"{destination_dir}/{source.name}")

                # print(source)
                # print(destination_dir)
                # print("############")

                # if not destination_dir.exists():
                #     print("NO EXISTE")
                #     if source.is_dir():  # ES UN DIRECTORIO
                #         print("DIRECTORIO")
                #         shutil.copytree(source, destination_dir)
                #     else:  # ES UN ARCHIVO
                #         print("ARCHIVO")
                #         shutil.copy(source, destination_dir)

                #     continue

                # print("DESPUES")

                # if self.response_general == "cancel" or self.response_general == "skip":
                #     if self.check_button_all_files:
                #         print("Se cancela o skipea todos los archivos")
                #         dialog.close()
                #         return

                # if self.response_general == "overwrite_date":
                #     source_datetime = datetime.fromtimestamp(source.stat().st_ctime)
                #     destination_datetime = datetime.fromtimestamp(
                #         destination_file.stat().st_ctime
                #     )
                #     print(source_datetime)
                #     print(destination_datetime)
                #     if source_datetime < destination_datetime:
                #         print("el archivo de origen es mayor")

                # if self.response_general == "overwrite_diff":
                #     print(self.response_general)

                # if self.response_general == "rename":
                #     print(self.response_general)

                # dialog.close()
                # selected_items.remove(item)
                # if len(selected_items) != 0:
                #     self.open_overwrite_dialog(parent, explorer_dst, selected_items)

        overwrite_dialog = Overwrite_dialog(parent)
        overwrite_dialog.present()
        overwrite_dialog.connect("response", on_response)

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
