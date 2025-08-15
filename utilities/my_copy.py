from utilities.i18n import _
from controls.Actions import Actions
from pathlib import Path
from multiprocessing import Process
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy_move import Selected_for_copy_move
from views.copying import Copying
from views.explorer import Explorer
from utilities.rename import Rename_Logic
from utilities.access_control import AccessControl
from utilities.file_manager import File_manager
from asyncio import Future
import gi
import os
import time
import shutil
import asyncio
import threading

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402


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
        self.access_control = AccessControl()
        self.file_manager = File_manager()

    def on_copy(
        self,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        selected_items: list = None,
        parent: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Start to copy files or directories.
        """
        if not selected_items:
            selected_items = explorer_src.get_selected_items_from_explorer()[1]

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        if not self.file_manager.check_free_space(selected_items, dst_dir):
            self.action.show_msg_alert(
                parent, _("No hay suficiente espacio en destino")
            )
            return

        if not self.access_control.validate_dst_write(
            selected_items,
            explorer_src,
            explorer_dst,
            dst_dir,
            parent,
        ):
            return

        if src_dir == dst_dir:
            self.action.show_msg_alert(
                parent, _("Intentar copiar un archivo a él mismo")
            )
            return

        duplicate = False
        asyncio.ensure_future(
            self.copy_proccess(
                parent,
                selected_items,
                dst_dir,
                explorer_src,
                explorer_dst,
                duplicate,
            )
        )

    def on_duplicate(
        self,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        parent: Gtk.ApplicationWindow,
    ) -> None:
        """
        Start to copy files or directories.
        """

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        dst_dir = explorer_dst.actual_path

        if not self.file_manager.check_free_space(selected_items, dst_dir):
            self.action.show_msg_alert(
                parent, _("No hay suficiente espacio en destino")
            )
            return

        if not self.access_control.validate_dst_write(
            selected_items,
            explorer_src,
            explorer_dst,
            dst_dir,
            parent,
        ):
            return

        duplicate = True
        asyncio.ensure_future(
            self.copy_proccess(
                parent,
                selected_items,
                dst_dir,
                explorer_src,
                explorer_dst,
                duplicate,
            )
        )

    async def copy_proccess(
        self,
        parent: Gtk.ApplicationWindow,
        selected_items: list,
        dst_dir: Path,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        duplicate: bool,
    ) -> None:
        """
        It scans the files or directories in the received list
        (selected_items) and filters them according to what is
        in the destination.
        """

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
                duplicate,
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
        self,
        parent: Gtk.ApplicationWindow,
        selected_items: list,
        dst_dir: Path,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        duplicate: bool,
    ) -> None:
        """
        It scans all directories and copies and creates them
        if they don't exist.It copies files that don't exist,
        and asks what to do if they do.

        """

        for src_info in selected_items:

            if not self.access_control.validate_src_read(
                src_info,
                parent,
            ):
                self.close_dialog_copying_proccess()
                return

            # On push cancel, return all
            if self.stop_all:
                return

            # Set name when use copy or duplicate option
            if duplicate:
                if src_info.is_dir():
                    dst_info = Path(f"{dst_dir}/{src_info.name}_copy")
                else:
                    file_name = src_info.name
                    split_name = list(file_name.rpartition("."))
                    split_name[0] = f"{split_name[0]}_copy"
                    return_name = "".join(split_name)
                    print(return_name)
                    dst_info = Path(f"{dst_dir}/{return_name}")
            else:
                dst_info = Path(f"{dst_dir}/{src_info.name}")

            bucle_src_error = Path(f"{src_info}/{src_info.name}")

            if dst_info.resolve().is_relative_to(bucle_src_error.resolve()):

                GLib.idle_add(
                    self.action.show_msg_alert,
                    parent,
                    _(
                        "No se puede copiar en esta ruta,"
                        " se genera bucle infinito."
                    ),
                )
                continue

            if src_info.is_dir():
                if not dst_info.exists():
                    os.mkdir(dst_info)

                if dst_info.exists():
                    new_selected_items = list(src_info.iterdir())
                    duplicate = False
                    self.iterate_folders(
                        parent,
                        new_selected_items,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                        duplicate,
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
                                    self.overwrite_dialog(
                                        parent, src_info, dst_info
                                    )
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

        GLib.idle_add(explorer_dst.load_new_path, dst_info.parent)
        self.close_dialog_copying_proccess()

    def close_dialog_copying_proccess(self):
        self.copying_dialog.close_copying()
        if self.thread_update_dialog.is_alive():
            self.progress_on = False
            self.thread_update_dialog.join()

    async def overwrite_dialog(
        self, parent: Gtk.ApplicationWindow, src_info: Path, dst_info: Path
    ) -> None:
        """
        Opens dialog to answer what to do if the file exists
        """

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

    def copy_file(self, src_info: Path, dst_info: Path) -> bool:
        """
        copies files from a src to its dst, returns true if
        copied, false otherwise.
        """

        # Use multiprocessing to terminae on cancel copy
        self.thread_copy = Process(
            target=shutil.copy, args=(src_info, dst_info)
        )
        self.thread_copy.start()
        self.thread_copy.join()

        if dst_info.exists():
            return True
        else:
            return False

    def overwrite_with_type(
        self,
        parent: Gtk.ApplicationWindow,
        src_info: Path,
        dst_info: Path,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        response_type: str,
    ) -> None:
        """
        Based on the value of response_type, perform one action or another
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
                    asyncio.ensure_future(
                        self.create_dialog_rename(parent, dst_info)
                    ),
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
                    _(
                        f"""El nombre del fichero ya existe\n
                    Destino:{self.new_name}\n
                    Se ha hecho  una copia con:\n
                    Source: {self.emergency_name}"""
                    ),
                )
            else:
                self.copying_dialog.set_labels(src_info, self.new_name)
                self.copy_file(src_info, self.new_name)

    def overwrite(
        self,
        parent: Gtk.ApplicationWindow,
        src_info: Path,
        dst_info: Path,
        explorer_dst: Explorer,
    ) -> None:
        """
        When you overwrite, it renames the old file until
        the new one is copied successfully.
        """
        dst_old_name = f"{dst_info}.old"
        dst_old_file = Path(dst_old_name)
        if dst_old_file.exists():
            os.remove(dst_old_file)
        os.rename(dst_info, dst_old_name)

        result = self.copy_file(src_info, dst_info)

        if result:
            os.remove(dst_old_file)
        else:
            os.remove(dst_info)
            os.rename(dst_old_file, dst_info)

    async def create_dialog_selected_for_copy_move(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        selected_items: list,
    ) -> Future[bool]:
        """
        Create dialog from the selected list to copy
        """

        selected_for_copy = Selected_for_copy_move(
            parent,
            explorer_src,
            explorer_dst,
            selected_items,
            _("Copiar"),
        )
        response = await selected_for_copy.wait_response_async()
        return response

    async def create_dialog_copying(
        self, parent: Gtk.ApplicationWindow
    ) -> Future[bool]:
        """
        Creates dialog showing information about the file being copied
        """
        self.copying_dialog = Copying(parent)
        self.copying_dialog.present()
        self.thread_iterater_folder.start()
        response = await self.copying_dialog.wait_response_async()
        return response

    async def create_dialog_rename(
        self, parent: Gtk.ApplicationWindow, dst_info: Path
    ) -> None:
        rename_logic = Rename_Logic()
        self.rename_response = await rename_logic.create_dialog_rename(
            parent, dst_info
        )
        if not self.rename_response:
            self.cancel_rename = True
        self.rename_event.set()

    def update_dialog_copying(self, parent: Gtk.ApplicationWindow) -> None:
        """
        Actualiza la  información que muestra el dialog Copying()
        """
        while self.progress_on:
            time.sleep(0.1)
            if self.copying_dialog is not None:
                GLib.idle_add(self.copying_dialog.update_labels)
