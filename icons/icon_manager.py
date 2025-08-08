import gi
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402


class IconManager:

    def __init__(self, win: "Explorer"):  # noqa: F821
        self.display = win.get_display()
        self.icon_theme = Gtk.IconTheme.get_for_display(self.display)
        self.ext_to_mime = self.load_mime_types()

    def get_folder_icon(self) -> Gtk.IconPaintable:
        """
        Get especifit folder icon
        """
        paintable_icon = self.icon_theme.lookup_icon(
            "folder",
            None,
            256,
            1,
            Gtk.TextDirection.LTR,
            Gtk.IconLookupFlags.FORCE_SYMBOLIC,
        )
        return paintable_icon

    def get_back_icon(self) -> Gtk.IconPaintable:
        """
        Get the specific icon to go back to a folder
        """
        paintable_icon = self.icon_theme.lookup_icon(
            "go-jump-rtl-symbolic",
            None,
            256,
            1,
            Gtk.TextDirection.LTR,
            Gtk.IconLookupFlags.FORCE_SYMBOLIC,
        )
        return paintable_icon

    def load_mime_types(self, path="/etc/mime.types") -> dict:
        """
        From mime.types, read line by line and return a
        dictionary key = extension.
        """
        ext_to_mime = {}
        with open(path, "r") as f:
            for line in f:
                if line.strip() == "" or line.startswith("#"):
                    continue
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                mime_type = parts[0]
                extensions = parts[1:]
                for ext in extensions:
                    ext_to_mime[ext] = mime_type
        return ext_to_mime

    def get_icon_name_for_mime(self, mime_type: str) -> str:
        """
        Returns a Gio.ThemeIcon based on its
        mime_type (a list of possible names)
        """

        icon = Gio.content_type_get_icon(mime_type)
        if isinstance(icon, Gio.ThemedIcon):
            names = icon.get_names()
            if names:
                return names[3]
        return None

    def get_icon_for_file(self, filepath: str) -> Gtk.IconPaintable:
        """
        Returns a paintable based on the mime type obtained
        from ext. If none exists, it will be of type text/plain.
        """
        ext = os.path.splitext(filepath)[1].lower().lstrip(".")
        mime = self.ext_to_mime.get(ext, "text/plain")
        icon_name = self.get_icon_name_for_mime(mime)
        if icon_name:
            paintable_icon = self.icon_theme.lookup_icon(
                icon_name,
                None,
                256,
                1,
                Gtk.TextDirection.LTR,
                Gtk.IconLookupFlags.FORCE_SYMBOLIC,
            )
        if paintable_icon:
            return paintable_icon
