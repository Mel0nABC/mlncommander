# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.actions import Actions
from pathlib import Path
from queue import Empty
from datetime import datetime
from views.pop_up_windows.overwrite_window import OverwriteWindow
from views.pop_up_windows.selected_for_copy_move import Selected_for_copy_move
from views.pop_up_windows.transfering_data import Transfering
from views.mlncommander_explorer import Explorer
from utilities.rename import Rename_Logic
from utilities.access_control import AccessControl
from utilities.file_manager import File_manager
from multiprocessing import Queue
from asyncio import Future
import gi
import os
import shutil
import asyncio
import threading


gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402


class MyCopyMove:

    def __init__(self):
        self.action = Actions()
        self.transfering_window = None
        self.response_dic = {}
        self.rename_response = None
        self.cancel_rename = False
        self.new_name = None
        self.all_files = False
        self.stop_all = False
        self.access_control = AccessControl()
        self.parent = None
        self.thread_copy = None
        self.explorer_src = None
        self.explorer_dst = None
        self.showed_msg_network_problem = False
        self.action_to_exec = None
        self.duplicate = None
        self.q = None
        self.overwrite_response = None

    def on_copy_or_move(
        self,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        selected_items: list = None,
        parent: Gtk.ApplicationWindow = None,
        action_str: str = None,
        action_copy: bool = True,
        duplicate: bool = None,
    ) -> None:
        """
        Start to copy files or directories.
        """
        self.action_to_exec = action_str
        self.parent = parent
        self.explorer_src = explorer_src
        self.explorer_dst = explorer_dst
        self.action_copy = action_copy
        self.duplicate = duplicate
        if not selected_items:
            selected_items = explorer_src.get_selected_items_from_explorer()[1]

        src_dir = explorer_src.actual_path
        dst_dir = explorer_dst.actual_path

        if not File_manager().check_free_space(selected_items, dst_dir):
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

        if not duplicate:
            if src_dir == dst_dir:
                text = _("un archivo a él mismo")
                self.action.show_msg_alert(
                    parent,
                    (f"{_("Intenta ")}{action_str} {text}"),
                )
                return

        asyncio.ensure_future(
            self.copy_proccess(
                parent,
                selected_items,
                dst_dir,
                explorer_src,
                explorer_dst,
                duplicate,
            ),
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

        self.iterator_thread = threading.Thread(
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
            target=self.update_dialog_transfering,
            args=(parent,),
        )
        self.thread_update_dialog.start()
        result = await self.create_dialog_transfering(parent)

        self.progress_on = False
        if not result:
            self.stop_all = True
            self.thread_copy.terminate()
            self.q.put({"ok": True, "error": "Se canceló el proceso"})

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

        def iterate_folders_worker(
            parent: Gtk.ApplicationWindow,
            selected_items: list,
            dst_dir: Path,
            explorer_src: Explorer,
            explorer_dst: Explorer,
            duplicate: bool,
        ) -> None:
            for src_info in selected_items:

                if not self.access_control.validate_src_read(
                    src_info,
                    parent,
                ):
                    self.close_dialog_transfering_proccess()
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
                        dst_info = Path(f"{dst_dir}/{return_name}")
                else:
                    dst_info = Path(f"{dst_dir}/{src_info.name}")

                bucle_src_error = Path(f"{src_info}/{src_info.name}")

                if dst_info.resolve().is_relative_to(
                    bucle_src_error.resolve()
                ):

                    GLib.idle_add(
                        self.action.show_msg_alert,
                        parent,
                        _(
                            "No se puede copiar en esta ruta,"
                            " se genera bucle infinito."
                        ),
                    )
                    continue

                # move section
                try:
                    if not self.action_copy:
                        os.rename(src_info, dst_info)
                        self.explorer_src.insert_log_line(
                            "MOVED", src_info, dst_info
                        )
                        continue
                except OSError:
                    pass

                if src_info.is_dir():
                    if not dst_info.exists():
                        os.mkdir(dst_info)

                    if dst_info.exists():
                        new_selected_items = list(src_info.iterdir())
                        duplicate = False
                        iterate_folders_worker(
                            parent,
                            new_selected_items,
                            dst_info,
                            explorer_src,
                            explorer_dst,
                            duplicate,
                        )
                else:
                    self.transfering_window.set_labels(src_info, dst_info)
                    if not dst_info.exists():
                        result = self.copy_file(src_info, dst_info)

                        # On stop copy, delete the last file,
                        # posible corruption
                        if self.stop_all:
                            if dst_info.exists():
                                dst_info.unlink()
                                pass
                        if not result:
                            return
                    else:
                        self.event_overwrite = threading.Event()
                        if not self.all_files:
                            GLib.idle_add(
                                lambda: (
                                    asyncio.ensure_future(
                                        self.overwrite_window(
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
                if not self.action_copy:
                    if not self.stop_all:
                        if src_info.is_dir():
                            src_info.rmdir()
                        else:
                            src_info.unlink()
                        self.explorer_src.insert_log_line(
                            "MOVED", src_info, dst_info
                        )

        iterate_folders_worker(
            parent,
            selected_items,
            dst_dir,
            explorer_src,
            explorer_dst,
            duplicate,
        )

        GLib.idle_add(explorer_src.load_new_path, explorer_src.actual_path)
        if explorer_dst.actual_path == dst_dir:
            GLib.idle_add(explorer_dst.load_new_path, dst_dir)
        GLib.idle_add(self.close_dialog_transfering_proccess)

        if not len(list(explorer_src.actual_path.iterdir())):
            GLib.idle_add(
                explorer_src.load_new_path, explorer_src.actual_path.parent
            )

    def close_dialog_transfering_proccess(self):
        self.transfering_window.on_finish_close()
        if self.thread_update_dialog.is_alive():
            self.progress_on = False
            self.thread_update_dialog.join()

    async def overwrite_window(
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

    async def create_response_overwrite(
        self, parent: Gtk.ApplicationWindow, src_info: Path, dst_info: Path
    ) -> asyncio.Future:
        self.overwrite_response = OverwriteWindow(parent, src_info, dst_info)
        response = await self.overwrite_response.wait_response_async()
        return response

    def copy_file(
        self,
        src_info: Path,
        dst_info: Path,
    ) -> bool:
        """
        copies files from a src to its dst, returns true if
        copied, false otherwise.
        """
        try:
            self.q = Queue()
            self.thread_copy = threading.Thread(
                target=self.copy_file_worker, args=(src_info, dst_info, self.q)
            )
            self.thread_copy.start()
            msg = self.q.get()
        except Empty:
            if self.thread_copy.exitcode == 0 and dst_info.exists():
                return True
            else:
                if not self.thread_copy.exitcode == -15:
                    GLib.idle_add(
                        self.action.show_msg_alert,
                        self.parent,
                        f"{_("Error al copiar:")} {self.thread_copy.exitcode}",
                    )
                if dst_info.exists():
                    dst_info.unlink()
                return False

        if msg["ok"]:
            if self.action_copy:
                if not self.stop_all:
                    if not self.duplicate:
                        self.explorer_src.insert_log_line(
                            "COPIED", src_info, dst_info
                        )
                    else:
                        self.explorer_src.insert_log_line(
                            "DUPLICATED", src_info, dst_info
                        )

            return True
        else:
            GLib.idle_add(
                self.action.show_msg_alert,
                self.parent,
                f"{_("Error al copiar:")} {msg["error"]}",
            )
            if dst_info.exists():
                dst_info.unlink()
            return False

    def copy_file_worker(
        self, src_info: Path, dst_info: Path, q: Queue
    ) -> dict:
        """
        copies files from a src to its dst, return dictionary
        """
        try:
            shutil.copy(src_info, dst_info)
            q.put({"ok": True, "error": None})
        except OSError as e:
            q.put({"ok": False, "error": e})
        except Exception as e:
            q.put({"ok": False, "error": e})

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
                        self.create_rename_window(parent, dst_info)
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
                self.transfering_window.set_labels(src_info, self.new_name)
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
                self.transfering_window.set_labels(src_info, self.new_name)
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
            self.action_to_exec,
        )
        response = await selected_for_copy.wait_response_async()
        return response

    async def create_dialog_transfering(
        self, parent: Gtk.ApplicationWindow
    ) -> Future[bool]:
        """
        Creates dialog showing information about the file being copied
        """
        self.transfering_window = Transfering(
            parent, self.action_to_exec, self.explorer_src, self.explorer_dst
        )

        if (
            parent.config.SWITCH_COPY_STATUS
            and self.action_to_exec == "copy"
            and not self.duplicate
        ):
            GLib.idle_add(self.transfering_window.to_background, None)
        elif (
            parent.config.SWITCH_DUPLICATE_STATUS
            and self.action_to_exec == "copy"
            and self.duplicate
        ):
            GLib.idle_add(self.transfering_window.to_background, None)
        elif (
            parent.config.SWITCH_MOVE_STATUS and self.action_to_exec == "move"
        ):
            GLib.idle_add(self.transfering_window.to_background, None)
        else:
            self.transfering_window.present()

        self.iterator_thread.start()
        response = await self.transfering_window.wait_response_async()
        return response

    async def create_rename_window(
        self, parent: Gtk.ApplicationWindow, dst_info: Path
    ) -> None:
        rename_logic = Rename_Logic()
        self.rename_response = await rename_logic.create_rename_window(
            parent, dst_info
        )
        if not self.rename_response:
            self.cancel_rename = True
        self.rename_event.set()

    def update_dialog_transfering(self, parent: Gtk.ApplicationWindow) -> None:
        """
        Actualiza la  información que muestra el dialog Copying()
        Update information to show dialog Copying() and move
        """
        while self.progress_on:
            try:
                if self.transfering_window is not None:

                    src_info = self.transfering_window.src_info

                    # update dst file on overwrite option
                    if self.overwrite_response:
                        if self.response_dic:
                            response_type = self.response_dic["response"]

                            if "overwrite" in response_type:
                                if Path(f"{src_info}.old").exists():
                                    dst_info = self.transfering_window.dst_info

                            if response_type == "rename":
                                dst_info = self.new_name
                    else:
                        dst_info = self.transfering_window.dst_info

                    src_store = True
                    dst_store = True
                    if src_info:
                        src_dir = src_info.parent
                        src_store = File_manager().get_path_list(src_dir)

                    if dst_info:
                        dst_dir = dst_info.parent
                        dst_store = File_manager().get_path_list(dst_dir)

                    if not src_store or not dst_store:

                        if not self.showed_msg_network_problem:
                            GLib.idle_add(
                                self.action.show_msg_alert,
                                self.parent,
                                (
                                    f"{_("Error al copiar:")} {dst_info}\n\n"
                                    f"{_("Puede deberse a una pérdida de red.")}"  # noqa: E501
                                    f"\n\n{_("si se recupera, se borrará")}"
                                    f"{_(" automáticamente el archivo corrupto.")}"  # noqa: E501
                                ),
                            )
                            self.showed_msg_network_problem = True
                        else:
                            self.showed_msg_network_problem = False
                        self.thread_copy.terminate()
                        if not src_store:
                            GLib.idle_add(
                                self.explorer_src.load_new_path, Path("/")
                            )
                        if not dst_store:
                            GLib.idle_add(
                                self.explorer_dst.load_new_path, Path("/")
                            )

                    src_size_text = 0
                    dst_size_text = 0

                    if src_info:
                        src_size_text = f"{src_info.stat().st_size}"
                    if dst_info:
                        dst_size_text = f"{dst_info.stat().st_size}"

                    GLib.idle_add(
                        self.transfering_window.update_labels,
                        src_size_text,
                        dst_size_text,
                    )
            except FileNotFoundError as e:
                print(f"Very fast I dont have time to update!!: {e}")
