# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT

from utilities.i18n import _
from pathlib import Path
import subprocess
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

        win_dialog = Gtk.Window.new()
        win_dialog.set_title(_("Cerrando aplicación"))
        win_dialog.set_transient_for(win)
        win_dialog.set_modal(True)
        win_dialog.set_decorated(False)

        win_dialog.get_style_context().add_class("app_background")
        win_dialog.get_style_context().add_class("font")
        win_dialog.get_style_context().add_class("font-color")

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vertical_box.set_margin_top(20)
        vertical_box.set_margin_end(20)
        vertical_box.set_margin_bottom(20)
        vertical_box.set_margin_start(20)

        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        horizontal_box.set_margin_top(10)
        horizontal_box.set_hexpand(True)
        horizontal_box.set_halign(Gtk.Align.CENTER)

        text = _("¿Confirma que quieres cerrar la aplicación?")
        label = Gtk.Label.new(text)

        btn_accept = Gtk.Button.new_with_label(_("Aceptar"))
        btn_accept.set_margin_end(30)
        btn_cancel = Gtk.Button.new_with_label(_("Cancelar"))

        horizontal_box.append(btn_accept)
        horizontal_box.append(btn_cancel)

        vertical_box.append(label)
        vertical_box.append(horizontal_box)

        win_dialog.set_child(vertical_box)

        def on_accept(button: Gtk.Button) -> None:
            win.exit()

        def on_cancel(button: Gtk.Button) -> None:
            win_dialog.destroy()

        btn_accept.connect("clicked", on_accept)
        btn_cancel.connect("clicked", on_cancel)

        win_dialog.present()

    def open_rename_dialog(
        self,
        explorer_src: Gtk.ColumnView,
        win: Gtk.ApplicationWindow,
        popovermenu: Gtk.PopoverMenu = None,
    ) -> None:
        from utilities.rename import Rename_Logic

        rename_logic = Rename_Logic()
        if popovermenu:
            popovermenu.unparent()
        rename_logic.on_rename(explorer_src, win)

    def open_terminal(self, explorer: Gtk.ColumnView) -> None:
        path = explorer.actual_path
        try:
            terminal_command = explorer.get_root().config.TERMINAL_COMMAND

            cmd = terminal_command.split(" ")
            cmd.append(path)

            p = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if p.returncode != 0:
                error_text = _(
                    "Error al ejecutar la terminal, comprueba la bandera"
                )
                GLib.idle_add(self.show_msg_alert, self.parent, error_text)

        except Exception as e:
            print(f"Error al abrir terminal: {e}")
            text = _(f"Error al abrir la terminal: {e}")
            GLib.idle_add(self.show_msg_alert, self.parent, text)
