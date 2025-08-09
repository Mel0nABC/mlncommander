from __future__ import annotations
from controls.Actions import Actions
from pathlib import Path
from views.create_dir_dialog import Create_dir_dialog
from views.explorer import Explorer
import asyncio
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk  # noqa:E402


class Create:

    def __init__(self):
        self.action = Actions()

    def on_create_dir(
        self,
        explorer_dst: Explorer,
        other_explorer: Explorer,
        parent: Gtk.ApplicationWindow,
        button=None,
    ) -> None:
        """
        To create directory. if dir exist, warns
        """

        if not explorer_dst:
            self.action.show_msg_alert(parent, "Debe seleccionar explorador.")
            return

        dst_dir = explorer_dst.actual_path

        if not os.access(dst_dir, os.W_OK):
            self.action.show_msg_alert(
                parent,
                (
                    f"No tienes permiso de escritura en el directorio de"
                    f" destino:\n\n{dst_dir}"
                ),
            )
            return False

        asyncio.ensure_future(
            self.on_create_dir_async(explorer_dst, other_explorer, parent)
        )

    async def on_create_dir_async(
        self,
        explorer_dst: Explorer,
        other_explorer: Explorer,
        parent: Gtk.ApplicationWindow,
    ) -> None:
        """
        Launches the dialog window to create a new directory
        """

        create_dir = Create_dir_dialog(parent, explorer_dst)
        response = await create_dir.wait_response_async()
        dst_dir = Path(f"{explorer_dst.actual_path}/{response}")

        if not response:
            return

        if explorer_dst.actual_path == dst_dir or not response.strip():
            self.action.show_msg_alert(
                parent, "Debes introducir algún nombre válido."
            )
            return

        if dst_dir.exists():
            self.action.show_msg_alert(
                parent, "El directorio que quiere crear, ya existe."
            )
            return

        if dst_dir.name == "None":
            return

        dst_dir.mkdir()
        explorer_dst.load_data(explorer_dst.actual_path)

        if other_explorer.actual_path == explorer_dst.actual_path:
            other_explorer.load_data(explorer_dst.actual_path)

        self.action.set_explorer_to_focused(explorer_dst, parent)

        new_n_row = 0
        for i, item in enumerate(explorer_dst.store):
            if dst_dir.name == item.name:
                new_n_row = i

        GLib.idle_add(
            explorer_dst.scroll_to, new_n_row, None, explorer_dst.flags
        )
