from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import sys, shutil, filecmp
import gi, os, time, asyncio


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

        if explorer_src.actual_path == explorer_dst.actual_path:
            self.show_msg_alert("Intentar copiar un archivo a él mismo")
            return

        selection = explorer_src.get_selection()
        selected_items = []
        for index in range(selection.get_n_items()):
            if selection.is_selected(index):
                selected_items.append(selection.get_item(index))

        self.copy(parent, explorer_src, explorer_dst, selected_items)

    def copy(self, parent, explorer_src, explorer_dst, selected_items):
        if not explorer_src:
            return

        if not explorer_dst:
            return

        if not selected_items:
            return

        asyncio.run(self.check_data(parent, explorer_src, explorer_dst, selected_items))

    async def check_data(self, parent, explorer_src, explorer_dst, selected_items):
        print("INICIO")
        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path
        exist_files_or_dir = False
        self.response_type = None
        self.all_files = False
        for i in selected_items:
            src_info = i.path_file
            dst_info = Path(f"{dst_dir}/{src_info.name}")
            print(src_info)
            print(dst_info)
            if dst_info.exists():
                if not dst_info.is_dir():
                    print("EXISTE EL ARCHIVO")
                    dialog_response = await self.create_dialog_overwrite(
                        parent, src_info, dst_info
                    )
                    print(dialog_response)
                else:
                    print(
                        "Es un directorio, hay que recorrerlo para comparar subdirectorios"
                    )
            else:
                # NO EXISTE EN DESTINO
                if not src_info.is_dir():
                    self.copy_progress("file", src_info, dst_info)
                else:
                    self.copy_progress("dir", src_info, dst_info)
            self.change_path(explorer_dst, dst_dir)

    async def create_dialog_overwrite(self, parent, src_info, dst_info):
        dialog = Overwrite_dialog(parent, src_info, dst_info)
        response = await dialog.wait_response_async()
        return response

    def copy_progress(self, type, src_info, dst_info):
        print("Para copiar archivos e ir indicando el progreso")
        if type == "file":
            print("Copiando archivos")
            shutil.copy(src_info, dst_info)
        else:
            print("Copiando directorios")

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
