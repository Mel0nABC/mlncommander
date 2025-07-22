from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class My_copy:

    def __init__(self):
        self.action = Actions()
        self.copying_dialog = None

    def on_copy(self, explorer_src, explorer_dst, parent):
        """
        Inicio para copiar ficheros o directorios.
        """

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        if not explorer_src:
            self.action.show_msg_alert(
                "Debe seleccionar un archivo o carpeta antes de intentar copiar."
            )
            return

        if not explorer_dst:
            self.action.show_msg_alert(
                "Ha ocurrido un problema con la ventana de destino,reinicie la aplicación."
            )
            return

        if src_dir == dst_dir:
            self.action.show_msg_alert("Intentar copiar un archivo a él mismo")
            return

        selected_items = self.action.get_selected_items_from_explorer(explorer_src)

        if not selected_items:
            return

        asyncio.ensure_future(
            self.copy_proccess(
                parent, selected_items, dst_dir, explorer_src, explorer_dst
            )
        )

    async def copy_proccess(
        self, parent, selected_items, dst_dir, explorer_src, explorer_dst
    ):
        """
        Recorre los ficheros o directorios de la lista recibida (selected_items) y los filtra según que hay  en destino
        """
        self.all_files = False
        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        response = await self.create_dialog_selected_for_copy(
            parent, explorer_src, explorer_dst, selected_items
        )

        if not response:
            return

        async def iterate_folders(
            parent, selected_items, dst_dir, explorer_src, explorer_dst
        ):
            for src_info in selected_items:
                dst_info = Path(f"{dst_dir}/{src_info.name}")
                bucle_src_error = Path(f"{src_info}/{src_info.name}")
                if dst_info.resolve().is_relative_to(bucle_src_error.resolve()):
                    self.action.show_msg_alert(
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
                            self.action.show_msg_alert(
                                f"Ha ocurrido un error al crear la ruta:\n\n{dst_info}"
                            )

                    else:

                        result = await self.init_copy_work(parent, src_info, dst_info)
                        if not result:
                            self.action.show_msg_alert(
                                "Se ha cancelado la copia de archivos"
                            )
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
        self.copying_dialog.destroy()
        self.action.change_path(explorer_dst, dst_dir)

    async def init_copy_work(self, parent, src_info, dst_info):
        """
        Inicia el proceso de copia
        """
        self.progress_on = True
        self.thread_update_dialog = threading.Thread(
            target=self.update_dialog_copying,
            args=(parent, src_info, dst_info),
        )
        self.thread_update_dialog.start()

        thread_copy_file = multiprocessing.Process(
            target=self.copy_file, args=(src_info, dst_info)
        )
        thread_copy_file.start()

        result = await self.create_dialog_copying(parent, src_info, dst_info)

        if self.thread_update_dialog.is_alive():
            self.progress_on = False
            self.thread_update_dialog.join()
        if thread_copy_file.is_alive():
            thread_copy_file.join()

        return result

    def copy_file(self, src_info, dst_info):
        """
        copia ficheros de un src a su dst
        """
        shutil.copy(src_info, dst_info)

    async def overwrite_response_dialog(self, parent, src_info, dst_info):
        """
        Ventana/Dialog para dar respuesta a las opciones cuando el fichero existe en destino
        """
        response_dic = {}
        dialog_response = await self.create_dialog_overwrite(parent, src_info, dst_info)
        response_dic["response"] = dialog_response["response"]
        response_dic["all_files"] = dialog_response["all_files"]

        return response_dic

    async def overwrite_with_type(
        self, parent, src_info, dst_info, explorer_src, explorer_dst, response_type
    ):
        """
        En base al valor de response_type, realiza una acción u otra
        """
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

    async def create_dialog_overwrite(self, parent, src_info, dst_info):
        """
        Crea dialog overwrite y devuelve su respuesta
        """

        dialog = Overwrite_dialog(parent, src_info, dst_info)
        response = await dialog.wait_response_async()
        return response

    async def create_dialog_selected_for_copy(
        self, parent, explorer_src, explorer_dst, selected_items
    ):
        """
        Crea dialog de la lista seleccionada para copiar
        """
        selected_for_copy = Selected_for_copy(
            parent, explorer_src, explorer_dst, selected_items
        )
        response = await selected_for_copy.wait_response_async()
        return response

    async def create_dialog_copying(self, parent, src_info, dst_info):
        """
        Crea dialog mostrando info del archivo que se está copiando
        """
        self.copying_dialog = Copying(parent, src_info, dst_info)
        self.copying_dialog.update_labels()
        response = await self.copying_dialog.wait_response_async()
        return response

    def update_dialog_copying(self, parent, src_info, dst_info):
        """
        Actualiza la  información que muestra el dialog Copying()
        """
        while self.progress_on:
            time.sleep(0.2)
            if self.copying_dialog is not None:
                GLib.idle_add(self.copying_dialog.update_labels)

    async def overwrite(self, parent, src_info, dst_info, explorer_dst):
        """
        Cuando va a sobre escribir, renombra  el archivo viejo hasta que se copie correctamente el nuevo
        """
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
                else:
                    os.remove(dst_info)
                    os.rename(dst_old_file, dst_info)
