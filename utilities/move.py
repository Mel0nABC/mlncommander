from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy_move import Selected_for_copy_move
from views.moving import Moving
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Move:
    def __init__(self, parent):
        self.action = Actions()
        self.parent = parent
        self.progress_on = False

    def on_move(self, explorer_src, explorer_dst):
        """
        TODO, Mover archivos o directorios
                - Si el fichero existe, pedir confirmación sobre escribir (sobrescribir, cancelar)
        """

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

        selected_items = self.action.get_selected_items_from_explorer(explorer_src)

        # self.iterate_folders(selected_items, explorer_src, explorer_dst)
        self.thread_iterater_folder = threading.Thread(
            target=self.iterate_folders,
            args=(selected_items, explorer_src, explorer_dst),
        )

        asyncio.ensure_future(
            self.create_dialog_moving(
                self.parent, explorer_src, explorer_dst, selected_items
            )
        )

    async def create_dialog_moving(
        self, parent, explorer_src, explorer_dst, selected_items
    ):
        selected_for_moving = Selected_for_copy_move(
            parent,
            explorer_src,
            explorer_dst,
            selected_items,
            "Listo para mover ..",
            "Mover",
        )
        response = await selected_for_moving.wait_response_async()

        if not response:
            return

        thread_update_dialog = threading.Thread(target=self.update_dialog_moving)

        self.moving_dialog = Moving(self.parent)
        self.moving_dialog.present()
        self.progress_on = True
        self.thread_iterater_folder.start()
        thread_update_dialog.start()
        response = await self.moving_dialog.wait_response_async()

        if self.thread_iterater_folder.is_alive():
            GLib.idle_add(self.thread_iterater_folder.join)
            self.moving_dialog.destroy()
        if thread_update_dialog.is_alive():
            self.progress_on = False
            GLib.idle_add(thread_update_dialog.join)

    def update_dialog_moving(self):
        while self.progress_on:
            time.sleep(0.1)
            if self.moving_dialog is not None:
                GLib.idle_add(self.moving_dialog.update_labels)

    def iterate_folders(self, selected_items, explorer_src, explorer_dst):
        dst_dir = explorer_dst.actual_path
        total_files, total_size = self.count_files_and_size(selected_items)

        for item in selected_items:
            src_info = item
            parent = item.parent
            dst_info = Path(f"{dst_dir}/{src_info.name}")
            self.moving_dialog.set_labels(src_info, dst_info)

            if str(parent) == str(dst_dir):
                self.action.show_msg_alert(
                    "Estás queriendo mover el contenido al mismo directorio"
                )
                continue

            if src_info == dst_dir:
                self.action.show_msg_alert(
                    "Estas intentando mover un directorio dentro de sí mismo"
                )
                continue

            if src_info.is_dir():
                if not dst_info.exists():
                    os.mkdir(dst_info)

                if dst_info.exists():
                    explorer_dst.load_new_path(dst_info)
                    new_selected_items = list(src_info.iterdir())
                    self.iterate_folders(new_selected_items, explorer_src, explorer_dst)
            else:
                shutil.move(src_info, dst_info)

            if src_info.exists() and src_info.is_dir():
                os.rmdir(src_info)

        self.moving_dialog.close_moving()

    def count_files_and_size(self, selected_items):
        total_files = 0
        total_size = 0

        for ruta in selected_items:
            if ruta.is_dir():
                for f in ruta.rglob("*"):

                    if f.is_file():
                        total_files += 1
                        total_size += f.stat().st_size
            else:
                total_files += 1
                total_size += ruta.stat().st_size
        # total_size_float = f"{(total_size / 1024 / 1024):.2f}"
        return total_files, total_size
