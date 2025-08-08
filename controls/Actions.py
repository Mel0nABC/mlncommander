from pathlib import Path
import gi
import sys
import subprocess

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa:")


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
            explorer.update_watchdog_path(path, explorer)
        except FileNotFoundError:
            text = "¡Advertencia! El fichero o directorio de destino no existe"
            GLib.idle_add(self.show_msg_alert, self.parent, text)

    def entry_change_path(
        self, entry: Gtk.Entry, explorer: "Explorer"  # noqa: F821
    ) -> None:
        """
        When changing directories by writing it by hand in the entry
        """
        path = Path(entry.get_text())
        self.change_path(explorer, path)

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
                    f"""Ha ocurrido algun problema al intentar ejecutar el
                     archivo:\n{path}""",
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
        self, parent: Gtk.ApplicationWindow, text_input: str
    ) -> None:
        """
        Generic alert message, the desired text is passed to it
        """
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            buttons=Gtk.ButtonsType.OK,
            message_type=Gtk.MessageType.WARNING,
            text=text_input,
        )
        dialog.connect("response", lambda d, r: d.destroy())
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
                explorer_right.selection.unselect_all()
                win.set_explorer_focused(explorer_left, explorer_right)

            else:
                explorer_right.focused = True
                explorer_left.focused = False
                explorer_left.selection.unselect_all()
                win.set_explorer_focused(explorer_right, explorer_left)
        except AttributeError as e:
            print(f"Error inicialización: {e}")
