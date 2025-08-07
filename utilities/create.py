from __future__ import annotations
from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.create_dir_dialog import Create_dir_dialog
from views.explorer import Explorer
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


class Create:

    def __init__(self):
        self.action = Actions()

    def on_create_dir(
        self,
        explorer_dst: Explorer,
        other_explorer: Explorer,
        parent: Window,
        button=None,
    ) -> None:
        """
        To create directory. if dir exist, warns
        """

        if not explorer_dst:
            self.action.show_msg_alert(parent, "Debe seleccionar explorador.")
            return

        asyncio.ensure_future(
            self.on_create_dir_async(explorer_dst, other_explorer, parent)
        )

    async def on_create_dir_async(
        self, explorer_dst: Explorer, other_explorer: Explorer, parent: Window
    ) -> None:
        create_dir = Create_dir_dialog(parent, explorer_dst)
        response = await create_dir.wait_response_async()
        dst_dir = Path(f"{explorer_dst.actual_path}/{response}")

        if explorer_dst.actual_path == dst_dir or not response.strip():
            self.action.show_msg_alert(parent, "Debes introducir algún nombre válido.")
            return

        if dst_dir.exists():
            self.action.show_msg_alert(
                parent, "El directorio que quiere crear, ya existe."
            )
            return

        if dst_dir.name == "None":
            return

        os.mkdir(dst_dir)
        explorer_dst.load_data(explorer_dst.actual_path)

        if other_explorer.actual_path == explorer_dst.actual_path:
            other_explorer.load_data(explorer_dst.actual_path)

        row_number = 0
        for index, item in enumerate(explorer_dst.store):
            if dst_dir == item.path_file:
                row_number = index
        explorer_dst.grab_focus()
        explorer_dst.scroll_to(row_number, None, explorer_dst.flags)
