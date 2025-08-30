# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.actions import Actions
from pathlib import Path
from asyncio import Future
from utilities.access_control import AccessControl
from views.explorer import Explorer
from views.selected_for_delete import Selected_for_delete
from views.deleting import Deleting
import asyncio
import threading
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa: E402


class Remove:

    def __init__(self):
        self.action = Actions()
        self.access_control = AccessControl()
        self.dialog_deleting = None
        self.stop_deleting = False

    def on_delete(
        self,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        parent: Gtk.ApplicationWindow,
    ) -> None:
        """
        Remove files or directory, no undo support

        """
        src_info = explorer_src.actual_path

        if not src_info.exists():
            self.action.show_msg_alert(
                parent,
                _(
                    """Ha surgido algún problema al
                 intentar eliminar la ubicacion seleccionada"""
                ),
            )

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        if not selected_items:
            self.action.show_msg_alert(
                parent, _("Debe seleccionar algún archivo o directorio.")
            )
            return

        asyncio.ensure_future(
            self.delete_select(
                parent, explorer_src, explorer_dst, selected_items
            )
        )

    async def delete_select(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        selected_items: list,
    ) -> None:
        """
        It asks for confirmation about what to delete and does
        so, deleting the contents of directories.
        """
        response = await self.create_dialog_selected_for_delete(
            parent, explorer_src, selected_items
        )
        if not response:
            return

        self.thread_update_deleting = threading.Thread(
            target=self.delete_now,
            args=(selected_items, explorer_src, explorer_dst, parent),
        )

        response = await self.create_dialog_deleting(
            parent, explorer_src.actual_path
        )

        if not response:
            self.stop_deleting = True
            self.action.show_msg_alert(
                parent,
                _("Se detubo el proceso de borrado antes de finalizar."),
            )

    def delete_now(
        self,
        selected_items: list,
        explorer_src: Explorer,
        explorer_dst: Explorer,
        parent: Gtk.ApplicationWindow,
    ) -> None:
        """
        Proccess to delete files or directorys, no undo option
        """

        def delete_worker(
            selected_items: list,
            explorer_src: Explorer,
            explorer_dst: Explorer,
            parent: Gtk.ApplicationWindow,
        ):

            for item in selected_items:

                if not self.access_control.validate_src_write(
                    selected_items,
                    explorer_src,
                    explorer_dst,
                    item.parent,
                    parent,
                ):

                    self.stop_remove_dialog(explorer_src, explorer_dst)
                    return

                # Validates When a browser is inside a subdirectory
                # of what is to be deleted
                if item.is_dir():
                    folder = item.resolve()
                    subfolder = explorer_dst.actual_path.resolve()
                    if subfolder.is_relative_to(folder):
                        GLib.idle_add(
                            explorer_dst.load_new_path,
                            explorer_src.actual_path,
                        )

                # To stop the thread if the delete is canceled
                if self.stop_deleting:
                    return

                GLib.idle_add(self.dialog_deleting.update_labels, item)

                if item.exists():
                    if item.is_dir():
                        try:
                            contents = list(item.iterdir())
                            if contents:
                                delete_worker(
                                    contents,
                                    explorer_src,
                                    explorer_dst,
                                    parent,
                                )
                            item.rmdir()
                        except Exception as e:
                            print(
                                f"❌ Error al eliminar directorio {item}: {e}"
                            )

                    else:
                        try:
                            item.unlink()
                        except Exception as e:
                            print(f"❌ Error al eliminar archivo {item}: {e}")

        delete_worker(selected_items, explorer_src, explorer_dst, parent)
        self.stop_remove_dialog(explorer_src, explorer_dst)

    def stop_remove_dialog(
        self, explorer_src: Explorer, explorer_dst: Explorer
    ) -> None:
        GLib.idle_add(self.dialog_deleting.finish_deleting)
        GLib.idle_add(explorer_src.load_new_path, explorer_src.actual_path)
        GLib.idle_add(explorer_src.scroll_to, 0, None, explorer_src.flags)

        if explorer_src.actual_path == explorer_dst.actual_path:
            GLib.idle_add(explorer_dst.load_new_path, explorer_dst.actual_path)

    async def create_dialog_selected_for_delete(
        self,
        parent: Gtk.ApplicationWindow,
        explorer_src: Explorer,
        selected_items: list,
    ) -> Future[bool]:
        """
        Displays the confirmation dialog before calling delete_now()
        """
        selected_for_delete = Selected_for_delete(
            parent, explorer_src, selected_items
        )
        response = await selected_for_delete.wait_response_async()
        return response

    async def create_dialog_deleting(
        self, parent: Gtk.ApplicationWindow, src_info: Path
    ) -> Future[bool]:
        """
        Creates dialog showing information about the file being deleted
        """
        self.dialog_deleting = Deleting(parent, src_info)
        self.thread_update_deleting.start()
        self.dialog_deleting.update_labels(src_info)
        response = await self.dialog_deleting.wait_response_async()
        return response
