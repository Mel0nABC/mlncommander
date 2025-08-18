# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from __future__ import annotations
from utilities.i18n import _
from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from utilities.access_control import AccessControl
from utilities.file_manager import File_manager
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy_move import Selected_for_copy_move
from views.moving import Moving
from utilities.rename import Rename_Logic
from views.explorer import Explorer
import os
import time
import shutil
import asyncio
import threading
from asyncio import Future
from typing import Any
from gi.repository import GLib, Gtk


class Move:
    def __init__(self, parent):
        self.action = Actions()
        self.file_manager = File_manager()
        self.parent = parent
        self.access_control = AccessControl()
        self.progress_on = False
        self.response_dic = {}
        self.response_type = ""
        self.all_files = ""

    def on_move(self, explorer_src: Explorer, explorer_dst: Explorer) -> None:
        """
        To move directory or files
        """

        selected_items = explorer_src.get_selected_items_from_explorer()[1]
        dst_dir = explorer_dst.actual_path

        if not self.file_manager.check_free_space(selected_items, dst_dir):
            self.action.show_msg_alert(
                self.parent, _("No hay suficiente espacio en destino")
            )
            return

        if not self.access_control.validate_dst_write(
            selected_items,
            explorer_src,
            explorer_dst,
            dst_dir,
            self.parent,
        ):
            return

        self.thread_iterater_folder = threading.Thread(
            target=self.iterate_folders,
            args=(selected_items, dst_dir, explorer_src, explorer_dst),
        )

        asyncio.ensure_future(
            self.create_dialog_moving(
                self.parent, explorer_src, explorer_dst, selected_items
            )
        )

    async def create_dialog_moving(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        selected_items: list,
    ) -> None:
        """
        Create dialog, show files or directorys to move and need
        response, accept or cancel
        """
        selected_for_moving = Selected_for_copy_move(
            parent,
            explorer_src,
            explorer_dst,
            selected_items,
            _("Mover"),
        )
        response = await selected_for_moving.wait_response_async()

        if not response:
            return

        thread_update_dialog = threading.Thread(
            target=self.update_dialog_moving
        )

        self.moving_dialog = Moving(self.parent)
        self.moving_dialog.present()
        self.progress_on = True
        self.thread_iterater_folder.start()
        thread_update_dialog.start()
        response = await self.moving_dialog.wait_response_async()

        self.progress_on = False

    def update_dialog_moving(self) -> None:
        """
        Updates information about transferred files and runs in a thread
        """
        while self.progress_on:
            time.sleep(0.1)
            if self.moving_dialog is not None:
                GLib.idle_add(self.moving_dialog.update_labels)

    def iterate_folders(
        self,
        selected_items: list,
        dst_dir: Path,
        explorer_src: Explorer,
        explorer_dst: Explorer,
    ) -> None:
        """
        Traverse all subdirectories if required, all in a new thread
        """

        total_files, total_size = self.count_files_and_size(selected_items)

        self.all_files = False
        for item in selected_items:

            if not self.access_control.validate_src_read(
                item,
                self.parent,
            ):
                GLib.idle_add(self.moving_dialog.close_moving)
                return

            if not self.progress_on:
                return

            src_info = item
            parent = item.parent
            dst_info = Path(f"{dst_dir}/{src_info.name}")

            if str(parent) == str(dst_dir):
                self.action.show_msg_alert(
                    self.parent,
                    _(
                        "Estás queriendo mover "
                        "el contenido al mismo directorio"
                    ),
                )
                continue

            if src_info == dst_dir:
                self.action.show_msg_alert(
                    self.parent,
                    _(
                        "Estas intentando mover "
                        "un directorio dentro de sí mismo"
                    ),
                )
                continue

            if src_info.is_dir():
                if not dst_info.exists():
                    os.mkdir(dst_info)

                if dst_info.exists():
                    new_selected_items = list(src_info.iterdir())
                    self.iterate_folders(
                        new_selected_items,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                    )
            else:
                self.moving_dialog.set_labels(src_info, dst_info)
                if not dst_info.exists():
                    shutil.move(src_info, dst_info)
                else:
                    self.event_overwrite = threading.Event()
                    if not self.all_files:
                        GLib.idle_add(
                            lambda: (
                                asyncio.ensure_future(
                                    self.overwrite_dialog(
                                        self.parent, src_info, dst_info
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
                        self.parent,
                        src_info,
                        dst_info,
                        explorer_src,
                        explorer_dst,
                        self.response_type,
                    )

            # GLib.idle_add(explorer_src.load_data, src_info.parent)
            # GLib.idle_add(explorer_dst.load_data, dst_info.parent)

            if src_info.exists() and src_info.is_dir():
                if self.response_type != "skip" and not self.all_files:
                    os.rmdir(src_info)
        GLib.idle_add(explorer_src.load_new_path, src_info.parent)
        GLib.idle_add(explorer_dst.load_new_path, dst_info.parent)
        GLib.idle_add(self.moving_dialog.close_moving)

    def overwrite_with_type(
        self,
        parent,
        src_info: Path,
        dst_info: Path,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        response_type: str,
    ) -> None:
        """
        Based on the value of response_type, perform one action or another
        """

        self.cancel_rename = False
        self.rename_response = ""
        if response_type == "overwrite":
            os.remove(dst_info)
            if not dst_info.exists():
                shutil.move(src_info, dst_info)

        if response_type == "overwrite_date":
            src_file_date = datetime.fromtimestamp(src_info.stat().st_ctime)
            dst_file_date = datetime.fromtimestamp(dst_info.stat().st_ctime)
            if src_file_date > dst_file_date:
                os.remove(dst_info)
                if not dst_info.exists():
                    shutil.move(src_info, dst_info)

        if response_type == "overwrite_diff":
            if src_info.stat().st_size != dst_info.stat().st_size:
                os.remove(dst_info)
                if not dst_info.exists():
                    shutil.move(src_info, dst_info)

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

            # Pause thread event

            self.rename_event.wait()

            # For if you choose to cancel rename
            if self.cancel_rename:
                return

            self.new_name = Path(f"{dst_info.parent}/{self.rename_response}")

            if self.new_name.exists():
                self.emergency_name = Path(f"{self.new_name}.copy")
                while self.emergency_name.exists():
                    self.emergency_name = Path(f"{self.emergency_name}.copy")
                self.moving_dialog.set_labels(src_info, self.new_name)
                shutil.move(src_info, self.emergency_name)
                GLib.idle_add(
                    self.action.show_msg_alert,
                    parent,
                    _(
                        f"""El nombre del fichero ya existe\nDestino:"
                    {self.new_name}\n"
                    Se ha hecho  una copia con:\nSource: {self.emergency_name}
                    """
                    ),
                )
            else:
                self.moving_dialog.set_labels(src_info, self.new_name)
                shutil.move(src_info, self.new_name)

    async def create_dialog_rename(
        self, parent: Gtk.ApplicationWindow, dst_info: Path
    ) -> None:
        """
        When file exist and select rename option, create dialog to set new name
        """
        rename_logic = Rename_Logic()
        self.rename_response = await rename_logic.create_dialog_rename(
            self.parent, dst_info
        )
        if not self.rename_response:
            self.cancel_rename = True
        self.rename_event.set()

    async def overwrite_dialog(
        self, parent, src_info: Path, dst_info: Path
    ) -> None:

        dialog_response = await self.create_response_overwrite(
            parent, src_info, dst_info
        )
        self.response_dic["response"] = dialog_response["response"]
        self.response_dic["all_files"] = dialog_response["all_files"]
        self.event_overwrite.set()

    async def create_response_overwrite(
        self, parent, src_info: Path, dst_info: Path
    ) -> Future[Any]:
        """
        Overwrite dialog, show all options
        """
        dialog = Overwrite_dialog(parent, src_info, dst_info)
        response = await dialog.wait_response_async()
        return response

    def count_files_and_size(self, selected_items: list) -> tuple[int, int]:
        """
        Counts files and adds up their size
        """

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
        return total_files, total_size
