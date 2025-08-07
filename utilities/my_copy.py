from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy_move import Selected_for_copy_move
from views.copying import Copying
from utilities.rename import Rename_Logic
import gi, os, time, shutil, asyncio, threading, multiprocessing
from threading import Event
from gi.repository import GLib
from multiprocessing import Process


class My_copy:

    def __init__(self):
        self.action = Actions()
        self.copying_dialog = None
        self.response_dic = {}
        self.rename_response = None
        self.cancel_rename = False
        self.new_name = None
        self.all_files = False
        self.stop_all = False

    def on_copy(self, explorer_src, explorer_dst, parent):
        """
        Inicio para copiar ficheros o directorios.
        """

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        if not selected_items:
            self.action.show_msg_alert(
                parent, "Debe seleccionar algún archivo o directorio."
            )
            return

        if not explorer_dst:
            self.action.show_msg_alert(
                parent,
                "Ha ocurrido un problema con la ventana de destino,reinicie la aplicación.",
            )
            return

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        if src_dir == dst_dir:
            self.action.show_msg_alert(parent, "Intentar copiar un archivo a él mismo")
            return

        if not selected_items:
            self.action.show_msg_alert(
                parent, "Debe seleccionar algún archivo o directorio."
            )
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

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        response = await self.create_dialog_selected_for_copy_move(
            parent, explorer_src, explorer_dst, selected_items
        )
        if not response:
            return

        self.progress_on = True

        self.thread_iterater_folder = threading.Thread(
            target=self.iterate_folders,
            args=(
                parent,
                selected_items,
                dst_dir,
                explorer_src,
                explorer_dst,
            ),
        )

        self.thread_update_dialog = threading.Thread(
            target=self.update_dialog_copying,
            args=(parent,),
        )
        self.thread_update_dialog.start()

        result = await self.create_dialog_copying(parent)

        self.progress_on = False

        if not result:
            self.stop_all = True
            self.thread_copy.terminate()

    def iterate_folders(
        self, parent, selected_items, dst_dir, explorer_src, explorer_dst
    ):

        for src_info in selected_items:

            # On push cancel, return all
            if self.stop_all:
                return

            dst_info = Path(f"{dst_dir}/{src_info.name}")
            bucle_src_error = Path(f"{src_info}/{src_info.name}")

            if dst_info.resolve().is_relative_to(bucle_src_error.resolve()):

                GLib.idle_add(
                    self.action.show_msg_alert,
                    parent,
                    "No se puede copiar en esta ruta, se genera bucle infinito.",
                )
                continue

            if src_info.is_dir():
                if not dst_info.exists():
                    os.mkdir(dst_info)

                if dst_info.exists():
                    new_selected_items = list(src_info.iterdir())
                    self.iterate_folders(
                        parent,
                        new_selected_items,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                    )
            else:
                self.copying_dialog.set_labels(src_info, dst_info)
                if not dst_info.exists():
                    self.copy_file(src_info, dst_info)
                    # On stop copy, delete the last file, posible corruption
                    if self.stop_all:
                        if dst_info.exists():
                            dst_info.unlink()
                            pass
                else:
                    self.event_overwrite = threading.Event()
                    if not self.all_files:
                        GLib.idle_add(
                            lambda: (
                                asyncio.ensure_future(
                                    self.overwrite_dialog(parent, src_info, dst_info)
                                ),
                                False,
                            )[1]
                        )

                        self.event_overwrite.wait()

                        self.response_type = self.response_dic["response"]
                        self.all_files = self.response_dic["all_files"]

                    if self.response_type == "skip":
                        continue

                    self.overwrite_with_type(
                        parent,
                        src_info,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                        self.response_type,
                    )

            GLib.idle_add(explorer_dst.load_data, dst_info.parent)

        self.copying_dialog.close_copying()
        if self.thread_update_dialog.is_alive():
            self.progress_on = False
            self.thread_update_dialog.join()

    async def overwrite_dialog(self, parent, src_info, dst_info):
        dialog_response = await self.create_response_overwrite(
            parent, src_info, dst_info
        )
        self.response_dic["response"] = dialog_response["response"]
        self.response_dic["all_files"] = dialog_response["all_files"]
        self.event_overwrite.set()

    async def create_response_overwrite(self, parent, src_info, dst_info):
        dialog = Overwrite_dialog(parent, src_info, dst_info)
        response = await dialog.wait_response_async()
        return response

    def copy_file(self, src_info, dst_info):
        """
        copia ficheros de un src a su dst, devuelve true  si se copió , false si no.
        """

        # Use multiprocessing to terminae on cancel copy
        self.thread_copy = Process(target=shutil.copy, args=(src_info, dst_info))
        self.thread_copy.start()
        self.thread_copy.join()

        if dst_info.exists():
            return True
        else:
            return False

    def overwrite_with_type(
        self, parent, src_info, dst_info, explorer_src, explorer_dst, response_type
    ):
        """
        En base al valor de response_type, realiza una acción u otra
        """

        if response_type == "overwrite":
            self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "overwrite_date":
            src_file_date = datetime.fromtimestamp(src_info.stat().st_ctime)
            dst_file_date = datetime.fromtimestamp(dst_info.stat().st_ctime)
            if src_file_date > dst_file_date:
                self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "overwrite_diff":
            if src_info.stat().st_size != dst_info.stat().st_size:
                self.overwrite(parent, src_info, dst_info, explorer_dst)

        if response_type == "rename":
            self.rename_event = threading.Event()

            GLib.idle_add(
                lambda: (
                    asyncio.ensure_future(self.create_dialog_rename(parent, dst_info)),
                    False,
                )[1]
            )

            # Event to generate pause in the thread
            self.rename_event.wait()

            # Skips item if renaming a file or folder is canceled
            if self.cancel_rename:
                return

            self.new_name = Path(f"{dst_info.parent}/{self.rename_response}")

            if self.new_name.exists():
                self.emergency_name = Path(f"{self.new_name}.copy")
                while self.emergency_name.exists():
                    self.emergency_name = Path(f"{self.emergency_name}.copy")
                self.copying_dialog.set_labels(src_info, self.new_name)
                self.copy_file(src_info, self.emergency_name)
                GLib.idle_add(
                    self.action.show_msg_alert,
                    parent,
                    f"El nombre del fichero ya existe\nDestino:{self.new_name}\nSe ha hecho  una copia con:\nSource: {self.emergency_name}",
                )
            else:
                self.copying_dialog.set_labels(src_info, self.new_name)
                self.copy_file(src_info, self.new_name)

    def overwrite(self, parent, src_info, dst_info, explorer_dst):
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
                # TODO: COPY WITH COPY TREE, NO LONGER USED, NEED REFACTOR THIS SECTION
                shutil.copytree(src_info, dst_info)
                shutil.rmtree(dst_old_file)
            else:
                result = self.copy_file(src_info, dst_info)

                if result:
                    os.remove(dst_old_file)
                else:
                    os.remove(dst_info)
                    os.rename(dst_old_file, dst_info)

    async def create_dialog_selected_for_copy_move(
        self, parent, explorer_src, explorer_dst, selected_items
    ):
        """
        Crea dialog de la lista seleccionada para copiar
        """

        selected_for_copy = Selected_for_copy_move(
            parent,
            explorer_src,
            explorer_dst,
            selected_items,
            "Copiar",
        )
        response = await selected_for_copy.wait_response_async()
        return response

    async def create_dialog_copying(self, parent):
        """
        Crea dialog mostrando info del archivo que se está copiando
        """
        self.copying_dialog = Copying(parent)
        self.copying_dialog.present()
        self.thread_iterater_folder.start()
        response = await self.copying_dialog.wait_response_async()
        return response

    async def create_dialog_rename(self, parent, dst_info):
        rename_logic = Rename_Logic()
        self.rename_response = await rename_logic.create_dialog_rename(parent, dst_info)
        if not self.rename_response:
            self.cancel_rename = True
        self.rename_event.set()

    def update_dialog_copying(self, parent):
        """
        Actualiza la  información que muestra el dialog Copying()
        """
        while self.progress_on:
            time.sleep(0.1)
            if self.copying_dialog is not None:
                GLib.idle_add(self.copying_dialog.update_labels)
