# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from controls.actions import Actions
from views.mlncommander_explorer import Explorer
from pathlib import Path
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class Rename_Logic:

    def __init__(self):
        self.response = None
        self.action = Actions()

    def on_rename(
        self, explorer_src: Explorer, parent: Gtk.ApplicationWindow
    ) -> None:
        """
        Rename file or directory
        """

        msg_text = _(
            (
                "Debe seleccionar un archivo o"
                " carpeta antes de intentar renombrar."
            )
        )
        if not explorer_src:
            self.action.show_msg_alert(parent, msg_text)
            return

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        if not selected_items:
            self.action.show_msg_alert(parent, msg_text)
            return

        src_info = selected_items[0]
        from views.pop_up_windows.rename_window import RenameWindow

        src_name = src_info.name
        for i in explorer_src.get_last_child():
            for index, value in enumerate(i.observe_children()):
                if index == 1:
                    widget = value.get_first_child().get_first_child()
                    if isinstance(widget, Gtk.Label):
                        label_text = widget.get_text()
                        if src_name == label_text:
                            RenameWindow(
                                explorer_src.win,
                                explorer_src,
                                widget,
                                src_info,
                                self,
                            )

    def rename(self, path_src: Path, new_name: str) -> dict:
        new_path = Path(f"{path_src.parent}/{new_name}")
        if new_path.exists():
            return {"status": False, "msg": _("El nombre destino, ya existe")}

        try:
            os.rename(path_src, new_path)
        except Exception as e:
            return {"status": False, "msg": e}

        if new_path.exists():
            return {"status": True, "msg": "ok"}
