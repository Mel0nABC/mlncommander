# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
from entity.flags import Flags
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject  # noqa: E402


class General(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow, parent: Gtk.Window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # GENERAL CONSTANTS

        self.GENERAL_TITLE = _("Minimizar al iniciar")
        self.COPY_LABEL = _("Copiar")
        self.MOVE_LABEL = _("Mover")
        self.DUPLICATE_LABEL = _("Duplicar")
        self.COMPRESS_LABEL = _("Comprimir")
        self.UNCOMPRESS_LABEL = _("Descomprimir")
        self.LANGUAGE_LABEL = _("Selección de idioma")

        self.SWITCH_COPY_STATUS = win.config.SWITCH_COPY_STATUS
        self.SWITCH_MOVE_STATUS = win.config.SWITCH_MOVE_STATUS
        self.SWITCH_DUPLICATE_STATUS = win.config.SWITCH_DUPLICATE_STATUS
        self.SWITCH_COMPRESS_STATUS = win.config.SWITCH_COMPRESS_STATUS
        self.SWITCH_UNCOMPRESS_STATUS = win.config.SWITCH_UNCOMPRESS_STATUS

        self.LANGUAGE = win.config.LANGUAGE

        self.win = win
        self.parent = parent
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        grid_language = Gtk.Grid(column_spacing=1, row_spacing=5)
        self.title_language = Gtk.Label.new(self.LANGUAGE_LABEL)

        import App

        flags = Flags()

        flags_type = flags.get_flags()

        store_languages = Gio.ListStore.new(item_type=Flags)

        store_languages.append(flags_type["es"])

        path_locales = Path(App.LOCALE_DIR)
        for dir in path_locales.iterdir():
            if dir.is_dir() and len(dir.stem) == 2:
                # creamos objeto flags
                acronym = dir.stem
                if acronym == "en":
                    store_languages.append(flags_type["gb"])
                    store_languages.append(flags_type["us"])
                else:
                    store_languages.append(flags_type[acronym])

        dropdown_language = Gtk.DropDown.new(store_languages)

        self.set_language_dropdown(store_languages, dropdown_language)

        factory = Gtk.SignalListItemFactory()

        max_len = max(len(flag.country_name) for flag in store_languages)

        def bind(factory, list_item):
            flag = list_item.get_item()
            if flag is None:
                return

            grid = Gtk.Grid(column_spacing=10, row_spacing=5)

            lbl_1 = Gtk.Label.new(flag.country_name.ljust(max_len))
            lbl_1.set_xalign(0.0)
            lbl_1.set_size_request(200, -1)
            lbl_2 = Gtk.Label.new(flag.flag)

            grid.attach(lbl_1, 0, 0, 1, 1)
            grid.attach(lbl_2, 1, 0, 1, 1)

            list_item.set_child(grid)

        factory.connect("bind", bind)

        dropdown_language.set_factory(factory)

        dropdown_language.connect(
            "notify::selected-item", self.language_change
        )

        grid_language.attach(self.title_language, 0, 0, 1, 1)
        grid_language.attach(dropdown_language, 1, 1, 1, 1)

        # Minimize on startup section

        grid_minimize = Gtk.Grid(column_spacing=1, row_spacing=5)

        self.append(grid_language)
        self.append(grid_minimize)

        self.title_label = Gtk.Label.new(self.GENERAL_TITLE)

        self.copy_label = Gtk.Label.new(self.COPY_LABEL)
        self.move_label = Gtk.Label.new(self.MOVE_LABEL)
        self.duplicate_label = Gtk.Label.new(self.DUPLICATE_LABEL)
        self.compress_label = Gtk.Label.new(self.COMPRESS_LABEL)
        self.uncompress_label = Gtk.Label.new(self.UNCOMPRESS_LABEL)

        self.copy_label.set_halign(Gtk.Align.START)
        self.move_label.set_halign(Gtk.Align.START)
        self.duplicate_label.set_halign(Gtk.Align.START)
        self.compress_label.set_halign(Gtk.Align.START)
        self.uncompress_label.set_halign(Gtk.Align.START)

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

        grid_minimize.attach(self.title_label, 0, 0, 1, 1)

        grid_minimize.attach(self.copy_label, 1, 1, 1, 1)
        grid_minimize.attach(copy_switch, 2, 1, 1, 1)

        grid_minimize.attach(self.move_label, 1, 2, 1, 1)
        grid_minimize.attach(move_switch, 2, 2, 1, 1)

        grid_minimize.attach(self.duplicate_label, 1, 3, 1, 1)
        grid_minimize.attach(duplicate_switch, 2, 3, 1, 1)

        grid_minimize.attach(self.compress_label, 1, 4, 1, 1)
        grid_minimize.attach(comrpess_switch, 2, 4, 1, 1)

        grid_minimize.attach(self.uncompress_label, 1, 5, 1, 1)
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

    def language_change(
        self, dropdrown: Gtk.DropDown, pspec: GObject.GParamSpec
    ) -> None:
        flag = dropdrown.get_selected_item()
        self.win.config.LANGUAGE = flag.acronym.lower()
        self.win.load_env_language()
        self.win.reload_for_language()

    def set_language_dropdown(
        self, store_languages: Gio.ListStore, dropdown_language: Gtk.DropDown
    ) -> None:
        for index, item in enumerate(store_languages):
            if self.LANGUAGE in item.acronym.lower():
                dropdown_language.set_selected(index)
