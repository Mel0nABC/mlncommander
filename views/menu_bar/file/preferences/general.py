# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class General(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # GENERAL CONSTANTS

        self.GENERAL_TITLE = _("Minimizar al iniciar")
        self.COPY_LABEL = _("Copiar")
        self.MOVE_LABEL = _("Mover")
        self.DUPLICATE_LABEL = _("Duplicar")
        self.COMPRESS_LABEL = _("Comprimir")
        self.UNCOMPRESS_LABEL = _("Descomprimir")

        # GENERAL

        self.SWITCH_COPY_STATUS = win.config.SWITCH_COPY_STATUS
        self.SWITCH_MOVE_STATUS = win.config.SWITCH_MOVE_STATUS
        self.SWITCH_DUPLICATE_STATUS = win.config.SWITCH_DUPLICATE_STATUS
        self.SWITCH_COMPRESS_STATUS = win.config.SWITCH_COMPRESS_STATUS
        self.SWITCH_UNCOMPRESS_STATUS = win.config.SWITCH_UNCOMPRESS_STATUS

        self.win = win
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        grid_lenguage = Gtk.Grid(column_spacing=1, row_spacing=5)
        # copy_label = Gtk.Label.new(Preferences.COPY_LABEL)

        # Minimize on startup section

        grid_minimize = Gtk.Grid(column_spacing=1, row_spacing=5)

        self.append(grid_lenguage)
        self.append(grid_minimize)

        title_label = Gtk.Label.new(self.GENERAL_TITLE)

        copy_label = Gtk.Label.new(self.COPY_LABEL)
        move_label = Gtk.Label.new(self.MOVE_LABEL)
        duplicate_label = Gtk.Label.new(self.DUPLICATE_LABEL)
        compress_label = Gtk.Label.new(self.COMPRESS_LABEL)
        uncompress_label = Gtk.Label.new(self.UNCOMPRESS_LABEL)

        copy_label.set_halign(Gtk.Align.START)
        move_label.set_halign(Gtk.Align.START)
        duplicate_label.set_halign(Gtk.Align.START)
        compress_label.set_halign(Gtk.Align.START)
        uncompress_label.set_halign(Gtk.Align.START)

        copy_switch = Gtk.Switch.new()
        copy_switch.set_active(self.SWITCH_COPY_STATUS)
        copy_switch.connect("state-set", self.on_press_any)

        move_switch = Gtk.Switch.new()
        move_switch.set_active(self.SWITCH_MOVE_STATUS)
        move_switch.connect("state-set", self.on_press_any)

        duplicate_switch = Gtk.Switch.new()
        duplicate_switch.set_active(self.SWITCH_DUPLICATE_STATUS)
        duplicate_switch.connect("state-set", self.on_press_any)

        comrpess_switch = Gtk.Switch.new()
        comrpess_switch.set_active(self.SWITCH_COMPRESS_STATUS)
        comrpess_switch.connect("state-set", self.on_press_any)

        uncompress_switch = Gtk.Switch.new()
        uncompress_switch.set_active(self.SWITCH_UNCOMPRESS_STATUS)
        uncompress_switch.connect("state-set", self.on_press_any)

        copy_switch.set_name("copy")
        move_switch.set_name("move")
        duplicate_switch.set_name("duplicate")
        comrpess_switch.set_name("compress")
        uncompress_switch.set_name("uncompress")

        copy_switch.set_hexpand(True)
        copy_switch.set_halign(Gtk.Align.CENTER)
        move_switch.set_hexpand(True)
        move_switch.set_halign(Gtk.Align.CENTER)
        duplicate_switch.set_hexpand(True)
        duplicate_switch.set_halign(Gtk.Align.CENTER)
        comrpess_switch.set_hexpand(True)
        comrpess_switch.set_halign(Gtk.Align.CENTER)
        uncompress_switch.set_hexpand(True)
        uncompress_switch.set_halign(Gtk.Align.CENTER)

        grid_minimize.attach(title_label, 0, 0, 1, 1)

        grid_minimize.attach(copy_label, 1, 1, 1, 1)
        grid_minimize.attach(copy_switch, 2, 1, 1, 1)

        grid_minimize.attach(move_label, 1, 2, 1, 1)
        grid_minimize.attach(move_switch, 2, 2, 1, 1)

        grid_minimize.attach(duplicate_label, 1, 3, 1, 1)
        grid_minimize.attach(duplicate_switch, 2, 3, 1, 1)

        grid_minimize.attach(compress_label, 1, 4, 1, 1)
        grid_minimize.attach(comrpess_switch, 2, 4, 1, 1)

        grid_minimize.attach(uncompress_label, 1, 5, 1, 1)
        grid_minimize.attach(uncompress_switch, 2, 5, 1, 1)

    def on_press_any(self, switch: Gtk.Switch, pspec: bool) -> None:

        if switch.get_name() == "copy":
            self.SWITCH_COPY_STATUS = pspec
            self.win.SWITCH_COPY_STATUS = pspec
        elif switch.get_name() == "move":
            self.SWITCH_MOVE_STATUS = pspec
            self.win.SWITCH_MOVE_STATUS = pspec
        elif switch.get_name() == "duplicate":
            self.SWITCH_DUPLICATE_STATUS = pspec
            self.win.SWITCH_DUPLICATE_STATUS = pspec
        elif switch.get_name() == "compress":
            self.SWITCH_COMPRESS_STATUS = pspec
            self.win.SWITCH_COMPRESS_STATUS = pspec
        elif switch.get_name() == "uncompress":
            self.SWITCH_UNCOMPRESS_STATUS = pspec
            self.win.SWITCH_UNCOMPRESS_STATUS = pspec
