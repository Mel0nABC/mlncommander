from pathlib import Path

from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.rename_dialog import Rename_dialog
from views.create_dir_dialog import Create_dir_dialog
from views.selected_for_copy import Selected_for_copy
from views.selected_for_delete import Selected_for_delete
from views.copying import Copying
import sys, shutil, filecmp
import gi, os, time, asyncio, threading, multiprocessing

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib


class Actions:

    def __init__(self):

        self.test = None
        self.source_file_general = None
        self.destination_file_general = None
        self.parent = None

        self.copying_dialog = None
        self.progress_on = False

    def set_parent(self, parent):
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

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        if not explorer_src:
            self.show_msg_alert(
                "Debe seleccionar un archivo o carpeta antes de intentar copiar."
            )
            return

        if not explorer_dst:
            self.show_msg_alert(
                "Ha ocurrido un problema con la ventana de destino,reinicie la aplicación."
            )
            return

        if src_dir == dst_dir:
            self.show_msg_alert("Intentar copiar un archivo a él mismo")
            return

        selected_items = self.get_selected_items_from_explorer(explorer_src)

        if not selected_items:
            return

        asyncio.ensure_future(
            self.check_data(parent, explorer_src, explorer_dst, selected_items)
        )

    def get_selected_items_from_explorer(self, explorer):
        selection = explorer.get_selection()
        selected_items = []
        for index in range(selection.get_n_items()):
            if selection.is_selected(index):
                selected_items.append(selection.get_item(index).path_file)

        return selected_items

    async def check_data(self, parent, explorer_src, explorer_dst, selected_items):
        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path
        exist_files_or_dir = False

        response = await self.create_dialog_selected_for_copy(
            parent, explorer_src, explorer_dst, selected_items
        )

        if not response:
            return

        await self.copy_proccess(
            parent, selected_items, dst_dir, explorer_src, explorer_dst
        )

        self.change_path(explorer_dst, dst_dir)

    async def copy_proccess(
        self, parent, selected_items, dst_dir, explorer_src, explorer_dst
    ):
        self.all_files = False

        async def iterate_folders(
            parent, selected_items, dst_dir, explorer_src, explorer_dst
        ):

            for src_info in selected_items:
                print(src_info)
                dst_info = Path(f"{dst_dir}/{src_info.name}")
                bucle_src_error = Path(f"{src_info}/{src_info.name}")
                if dst_info.resolve().is_relative_to(bucle_src_error.resolve()):
                    self.show_msg_alert(
                        "No se puede copiar en esta ruta, se genera bucle infinito."
                    )
                    continue

                # DESTINO NO EXISTE
                if not dst_info.exists():

                    if src_info.is_dir():
                        os.mkdir(dst_info)
                        if dst_info.exists():
                            if len(list(src_info.iterdir())) != 0:
                                selected_items_folder = src_info.iterdir()
                                await iterate_folders(
                                    parent,
                                    selected_items_folder,
                                    dst_info,
                                    explorer_src,
                                    explorer_dst,
                                )

                        else:
                            self.show_msg_alert(
                                f"Ha ocurrido un error al crear la ruta:\n\n{dst_info}"
                            )

                    else:

                        result = await self.init_copy_work(parent, src_info, dst_info)
                        if not result:
                            self.show_msg_alert("Se ha cancelado la copia de archivos")
                            self.change_path(explorer_dst, dst_dir)
                            self.change_path(explorer_src, src_dir)
                            return

                # DESTINO EXISTE
                else:
                    if src_info.is_dir():
                        if len(list(src_info.iterdir())) != 0:
                            selected_items_folder = src_info.iterdir()
                            await iterate_folders(
                                parent,
                                selected_items_folder,
                                dst_info,
                                explorer_src,
                                explorer_dst,
                            )

                    else:
                        if not self.all_files:
                            response_dic = await self.overwrite_response_dialog(
                                parent, src_info, dst_info
                            )
                            self.response_type = response_dic["response"]
                            self.all_files = response_dic["all_files"]

                        print(f"{self.response_type} -- {self.all_files}")
                        await self.overwrite_with_type(
                            parent,
                            src_info,
                            dst_info,
                            explorer_src,
                            explorer_dst,
                            self.response_type,
                        )

        await iterate_folders(
            parent, selected_items, dst_dir, explorer_src, explorer_dst
        )

    async def iterate_subfolders_to_copy_and_overwrite(
        self, parent, selected_items, dst_dir, explorer_src, explorer_dst, response_type
    ):

        async def subfolders(
            parent, selected_items, dst_dir, explorer_src, explorer_dst, response_type
        ):

            for item in selected_items:
                print(item)
                src_info = item
                if src_info.is_dir():
                    dst_info = Path(f"{dst_dir}/{src_info.name}")
                    if not dst_info.exists():
                        os.mkdir(dst_info)
                    else:
                        new_timestamp = time.mktime(
                            time.strptime("2023-01-01", "%Y-%m-%d")
                        )
                        # Cambiar fecha de acceso y modificación
                        os.utime(dst_info, (new_timestamp, new_timestamp))
                    subfolders(
                        parent, src_info.iterdir(), dst_info, explorer_src, explorer_dst
                    )

                else:
                    dst_info = Path(f"{dst_dir}/{src_info.name}")

                    await self.overwrite_with_type(
                        parent,
                        src_info,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                        response_type,
                    )

        await subfolders(
            parent, selected_items, dst_dir, explorer_src, explorer_dst, response_type
        )
        self.change_path(explorer_src, explorer_src.actual_path)
        self.change_path(explorer_dst, explorer_dst.actual_path)

    async def init_copy_work(self, parent, src_info, dst_info):
        print("INIC COPY WORK")
        self.progress_on = True
        thread_update_dialog = threading.Thread(
            target=self.update_dialog_copying,
            args=(parent, src_info, dst_info),
        )
        thread_update_dialog.start()

        thread_copy_file = multiprocessing.Process(
            target=self.copy_file, args=(src_info, dst_info)
        )
        thread_copy_file.start()

        result = await self.create_dialog_copying(parent, src_info, dst_info)
        if not result:
            if thread_update_dialog.is_alive():
                self.progress_on = False
                thread_update_dialog.join()
            if thread_copy_file.is_alive():
                thread_copy_file.terminate()
                thread_copy_file.join()
        return result

    def copy_file(self, src_info, dst_info):
        shutil.copy(src_info, dst_info)

    async def overwrite_response_dialog(self, parent, src_info, dst_info):
        response_dic = {}
        dialog_response = await self.create_dialog_overwrite(parent, src_info, dst_info)
        response_dic["response"] = dialog_response["response"]
        response_dic["all_files"] = dialog_response["all_files"]

        return response_dic

    async def overwrite_with_type(
        self, parent, src_info, dst_info, explorer_src, explorer_dst, response_type
    ):
        print(f"OVERWRITE WITH TYPE: {response_type}")
        if response_type == "overwrite":
            await self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "overwrite_date":
            src_file_date = datetime.fromtimestamp(src_info.stat().st_ctime)
            dst_file_date = datetime.fromtimestamp(dst_info.stat().st_ctime)
            if src_file_date > dst_file_date:
                await self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "overwrite_diff":
            if src_info.stat().st_size != dst_info.stat().st_size:
                await self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "rename":
            rename_response = await self.create_dialog_rename(parent, dst_info)
            if dst_info.name != rename_response:
                new_name = Path(f"{dst_info.parent}/{rename_response}")
                await self.init_copy_work(parent, src_info, new_name)

    async def create_dialog_rename(self, parent, dst_info):
        rename_dialog = Rename_dialog(parent, dst_info)
        response = await rename_dialog.wait_response_async()
        return response

    async def create_dialog_overwrite(self, parent, src_info, dst_info):
        dialog = Overwrite_dialog(parent, src_info, dst_info)
        response = await dialog.wait_response_async()
        return response

    async def create_dialog_selected_for_copy(
        self, parent, explorer_src, explorer_dst, selected_items
    ):
        selected_for_copy = Selected_for_copy(
            parent, explorer_src, explorer_dst, selected_items
        )
        response = await selected_for_copy.wait_response_async()
        return response

    async def create_dialog_selected_for_delete(
        self, parent, explorer_src, explorer_dst, selected_items
    ):
        selected_for_delete = Selected_for_delete(
            parent, explorer_src, explorer_dst, selected_items
        )
        response = await selected_for_delete.wait_response_async()
        return response

    async def create_dialog_copying(self, parent, src_info, dst_info):
        self.copying_dialog = Copying(parent, src_info, dst_info)
        self.copying_dialog.update_labels()
        response = await self.copying_dialog.wait_response_async()
        return response

    def update_dialog_copying(self, parent, src_info, dst_info):
        while self.progress_on:
            time.sleep(0.2)
            if self.copying_dialog is not None:
                GLib.idle_add(self.copying_dialog.update_labels)

    async def overwrite(self, parent, src_info, dst_info, explorer_dst):
        # print(f"OVERWRITE:\n{src_info}\n{dst_info}")
        dst_old_name = f"{dst_info}.old"
        dst_old_file = Path(dst_old_name)
        if dst_old_file.exists():
            os.remove(dst_old_file)
        os.rename(dst_info, dst_old_name)

        if dst_old_file.exists():
            if src_info.is_dir():
                shutil.copytree(src_info, dst_info)
                shutil.rmtree(dst_old_file)
            else:
                result = await self.init_copy_work(parent, src_info, dst_info)
                if result:
                    os.remove(dst_old_file)

        self.change_path(explorer_dst, explorer_dst.actual_path)

    def on_create_dir(self, explorer_dst, explorer_no_focused, parent, button=None):
        """
        TODO, para crear un directorio:
            - Si el directorio ya existe, que avise.
        """
        asyncio.ensure_future(
            self.on_create_dir_async(explorer_dst, explorer_no_focused, parent)
        )

    async def on_create_dir_async(self, explorer_focused, explorer_nofocused, parent):
        create_dir = Create_dir_dialog(parent, explorer_focused)
        response = await create_dir.wait_response_async()
        dst_dir = Path(f"{explorer_focused.actual_path}/{response}")

        if explorer_focused.actual_path == dst_dir or not response.strip():
            self.show_msg_alert("Debes introducir algún nombre válido.")
            return

        if dst_dir.exists():
            self.show_msg_alert("El directorio que quiere crear, ya existe.")
            return

        if dst_dir.name == "None":
            return

        os.mkdir(dst_dir)
        self.change_path(explorer_focused, explorer_focused.actual_path)
        if explorer_focused.actual_path == explorer_nofocused.actual_path:
            self.change_path(explorer_nofocused, explorer_nofocused.actual_path)

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

    def on_rename(self, explorer_focused, explorer_nofocused):
        """
        TODO, renombrar archivos o directorios.
        Si el archivo existe:
            - Cancelar
            - Remplazar
        """

        return

    def on_delete(self, explorer_focused, explorer_nofocused, parent):
        """
        TODO ,para eliminar archivos y directorios.
                - pedir confirmación para borrar (eliminar, cancelar)
                - Se hará que la recursividad pida confirmación, avisando que se perderá todo. Justo después de darle a eliminar.
        """
        src_info = explorer_focused.actual_path

        if not src_info.exists():
            self.show_msg_alert(
                "Ha surgido algún problema al intentar eliminar la ubicacion seleccionada"
            )

        selected_items = self.get_selected_items_from_explorer(explorer_focused)

        asyncio.ensure_future(
            self.iterate_subfolders_to_delete(
                parent, explorer_focused, explorer_nofocused, selected_items
            )
        )

    async def iterate_subfolders_to_delete(
        self, parent, explorer_focused, explorer_nofocused, selected_items
    ):

        response = await self.create_dialog_selected_for_delete(
            parent, explorer_focused, explorer_nofocused, selected_items
        )

        if not response:
            return

        for item in selected_items:

            if item.is_dir():
                if len(list(item.iterdir())) == 0:
                    os.rmdir(item)
                else:
                    iterate_subfolders(item.iterdir())
            else:
                os.remove(item)
            if item.is_dir():
                if len(list(item.iterdir())) == 0:
                    os.rmdir(item)

            dst_info = explorer_nofocused.actual_path
            if not explorer_nofocused.actual_path.exists():
                dst_info = dst_info.parent

            self.change_path(explorer_focused, explorer_focused.actual_path)
            self.change_path(explorer_nofocused, dst_info)

    def on_update_dir():
        """
        TODO, pulsar para actualizar directorio actual.
        """

        return
