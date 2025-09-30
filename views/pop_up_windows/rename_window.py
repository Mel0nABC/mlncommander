# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.rename import Rename_Logic
from controls.actions import Actions
from pathlib import Path
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class RenameWindow(Gtk.Popover):
    def __init__(
        self,
        win: Gtk.ApplicationWindow,
        parent: Gtk.Label,
        dst_info: Path,
        rename_logic: Rename_Logic,
    ):
        super().__init__()

        self.set_size_request(350, -1)

        self.win = win
        self.action = Actions()
        self.rename_logic = rename_logic
        self.dst_info = dst_info

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_margin_top(10)
        box.set_margin_end(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)

        label_txt = ""
        if dst_info.is_dir():
            label_txt = _("Renombrar directorio")
        else:
            label_txt = _("Renombrar fichero")

        label = Gtk.Label.new(label_txt)
        label_file = Gtk.Label.new(f"«{dst_info.name}»")
        self.entry = Gtk.Entry()
        self.entry.set_text(str(dst_info.name))
        self.entry.select_region(0, -1)
        button = Gtk.Button.new_with_label(_("Renombrar"))
        button.set_hexpand(False)
        button.set_halign(Gtk.Align.END)
        button.connect("clicked", self.on_rename)

        label.set_margin_bottom(5)
        label_file.set_margin_bottom(5)
        self.entry.set_margin_bottom(15)
        # button.set_margin_bottom(10)

        box.append(label)
        box.append(label_file)

        box.append(self.entry)
        box.append(button)

        self.set_parent(parent)
        self.set_child(box)

        self.popup()

        self.entry.connect("activate", self.on_rename)

    def on_rename(self, button: Gtk.Button = None) -> None:
        new_name = self.entry.get_text()

        if not new_name:
            self.popdown()
            return

        if new_name == self.dst_info.name:
            self.popdown()
        else:
            response = self.rename_logic.rename(self.dst_info, new_name)
            status = response["status"]
            msg = response["msg"]

        if not status:
            self.action.show_msg_alert(self.win, msg)

        self.popdown()
