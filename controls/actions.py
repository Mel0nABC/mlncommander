# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from pathlib import Path
import subprocess
import asyncio
import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib  # noqa:")


class Actions:

    def __init__(self):
        self.parent = None

    def set_parent(self, parent: Gtk.ApplicationWindow) -> None:
        self.parent = parent

    def on_exit(self, action, param: Gtk.ApplicationWindow) -> None:
        """
        To exis application from file menu
        """
        sys.exit(0)

    def change_path(
        self, explorer: "Explorer", path: Path  # noqa: F821
    ) -> None:
        """
        Access another directory.
        """
        try:
            if not path.exists():
                raise FileNotFoundError()
            explorer.load_new_path(path)
        except FileNotFoundError:
            text = _(
                "¡Advertencia! El fichero o directorio de destino no existe"
            )
            GLib.idle_add(self.show_msg_alert, self.parent, text)

    def entry_change_path(
        self, entry: Gtk.Entry, explorer: "Explorer"  # noqa: F821
    ) -> None:
        """
        When changing directories by writing it by hand in the entry
        """
        path = Path(entry.get_text())
        self.change_path(explorer, path)
        win = explorer.get_root()
        self.set_explorer_to_focused(explorer, win)

    def on_doble_click_or_enter(
        self,
        column_view: "Explorer",  # noqa: F821
        position: int,
        explorer: "Explorer",  # noqa: F821
        entry: Gtk.Entry,
    ) -> None:
        """
        Double-click a directory row and navigate to it. Click '..'
        and move one directory forward in the path. It doesn't currently
        open files.
        """
        file_or_directory = explorer.selection.get_item(position)

        path = file_or_directory.path_file
        type_str = file_or_directory.type

        if type_str == "FILE" or type_str == "LN BREAK":
            try:
                subprocess.run(["xdg-open", path])
            except Exception:
                self.show_msg_alert(
                    self.parent,
                    _(
                        f"""Ha ocurrido algun problema al intentar ejecutar el
                     archivo:\n{path}"""
                    ),
                )
            return

        if path.name == "..":
            actual_path_str = str(explorer.actual_path)
            folders = actual_path_str.split("/")
            folders.pop()

            if len(folders) == 1:
                output_folder = "/"
            else:
                output_folder = ""

                for i in folders:
                    if not i == "":
                        output_folder += f"/{i}"

            path = Path(output_folder)

        self.change_path(explorer, path)

    def show_msg_alert(
        self,
        parent: Gtk.ApplicationWindow,
        text_input: str,
        passwd: bool = None,
    ) -> None:
        """
        Generic alert message, the desired text is passed to it
        """
        # TODO: Change MessageDialog to AlertDialog, is deprecated
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text=text_input,
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.get_style_context().add_class("app_background")
        dialog.get_style_context().add_class("font")
        dialog.get_style_context().add_class("font-color")
        dialog.present()

    def set_explorer_to_focused(
        self,
        explorer_to_focused: "Explorer",  # noqa: F821
        win: Gtk.ApplicationWindow,
    ) -> None:
        """
        Managing which browser has focus
        """
        explorer_left = win.explorer_1
        explorer_right = win.explorer_2

        try:
            if explorer_to_focused == explorer_left:
                explorer_left.focused = True
                explorer_right.focused = False
                selection = explorer_right.selection
                if selection:
                    selection.unselect_all()
                win.set_explorer_focused(explorer_left, explorer_right)

            else:
                explorer_right.focused = True
                explorer_left.focused = False
                selection = explorer_left.selection
                if selection:
                    selection.unselect_all()
                win.set_explorer_focused(explorer_right, explorer_left)
        except AttributeError as e:
            print(f"Error inicialización: {e}")

    def close_with_question(self, *args, win: Gtk.ApplicationWindow) -> None:
        def on_close_response(dialog: Gtk.AlertDialog, task: Gio.Task):
            response = dialog.choose_finish(task)
            if not response:  # Accept
                win.exit()

        async def on_alarm(text: str):
            alert = Gtk.AlertDialog()
            alert.set_message(text)
            alert.set_buttons(["Aceptar", "Cancelar"])
            alert.set_cancel_button(1)
            alert.set_default_button(1)
            await alert.choose(win, None, on_close_response)

        text = _("¿Confirma que quieres cerrar la aplicación?")

        asyncio.ensure_future(on_alarm(text))
