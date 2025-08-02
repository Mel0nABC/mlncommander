import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, GLib

class IconManager:

    def __init__(self,win):
        self.display = win.get_display()
        self.icon_theme = Gtk.IconTheme.get_for_display(self.display)

    def get_folder_icon(self):
        paintable_icon = self.icon_theme.lookup_icon(
            "folder",
            None,
            256,
            1,
            Gtk.TextDirection.LTR,
            Gtk.IconLookupFlags.FORCE_SYMBOLIC,
        )
        return paintable_icon

    def get_file_icon(self):
        paintable_icon = self.icon_theme.lookup_icon(
            "text-x-generic-symbolic",
            None,
            256,
            1,
            Gtk.TextDirection.LTR,
            Gtk.IconLookupFlags.FORCE_SYMBOLIC,
        )
        return paintable_icon


    def get_back_icon(self):
        paintable_icon = self.icon_theme.lookup_icon(
            "go-jump-rtl-symbolic",
            None,
            256,
            1,
            Gtk.TextDirection.LTR,
            Gtk.IconLookupFlags.FORCE_SYMBOLIC,
        )
        return paintable_icon