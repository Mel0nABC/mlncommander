from controls.Actions import Actions

from pathlib import Path
import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa: E402


class AccessControl:

    def __init__(self):
        self.action = Actions()

    def validate_dst_write(
        self,
        selected_items: list,
        explorer_src: "Explorer",  # noqa: F821
        explorer_dst: "Explorer",  # noqa: F821
        dst_dir: Path,
        parent: Gtk.ApplicationWindow,
    ) -> bool:
        """
        Validate if copy continue
        """
        if not selected_items:
            GLib.idle_add(
                self.action.show_msg_alert,
                parent,
                "Debe seleccionar algún archivo o directorio.",
            )
            return False

        if not explorer_dst:
            GLib.idle_add(
                self.action.show_msg_alert,
                parent,
                (
                    "Ha ocurrido un problema con la"
                    " ventana de destino,reinicie la aplicación."
                ),
            )
            return False

        if not os.access(dst_dir, os.W_OK):
            GLib.idle_add(
                self.action.show_msg_alert,
                parent,
                (
                    f"No tienes permiso de escritura en el directorio de"
                    f" destino:\n\n{dst_dir}\n\n"
                    f"La acción no puede realizarse"
                ),
            )
            return False

        return True

    def validate_src_write(
        self,
        selected_items: list,
        explorer_src: "Explorer",  # noqa: F821
        explorer_dst: "Explorer",  # noqa: F821
        dst_dir: Path,
        parent: Gtk.ApplicationWindow,
    ) -> bool:
        """
        Validate if copy continue
        """
        if not os.access(dst_dir, os.W_OK):
            GLib.idle_add(
                self.action.show_msg_alert,
                parent,
                (
                    f"No tienes permiso de escritura en el directorio de"
                    f" origen:\n\n{dst_dir}\n\n"
                    f"La acción no puede realizarse"
                ),
            )
            return False

        return True

    def validate_src_read(
        self,
        src_dir_file: Path,
        parent: Gtk.ApplicationWindow,
    ) -> bool:
        if not os.access(src_dir_file, os.R_OK):
            GLib.idle_add(
                self.action.show_msg_alert,
                parent,
                (
                    f"No tienes permiso de lectura sobre el origen:\n\n"
                    f"{src_dir_file}\n\n"
                    f"Se detiene el proceso."
                ),
            )
            return False

        return True
