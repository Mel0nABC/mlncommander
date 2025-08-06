# gi, módulo que permite usar bibliotecas GTK en python.

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

from controls.Actions import Actions
from controls import Action_keys
from views.menu_bar import Menu_bar
from views.header import header
from views.explorer import Explorer
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.move import Move
from utilities.rename import Rename_Logic
from pathlib import Path
from icons.icon_manager import IconManager
import tkinter as tk
import os


class Window(Gtk.ApplicationWindow):

    def __init__(self, app, action):
        super().__init__(application=app)

        self.action = action
        self.explorer_src = None
        self.explorer_dst = None
        self.my_watchdog = None
        self.entry_margin = 10
        self.horizontal_button_list_margin = 8
        self.scroll_1_margin = 10
        self.CONFIG_FILE = Path("./config.conf")
        self.EXP_1_PATH = ""
        self.EXP_2_PATH = ""

        # We load the configuration, to send necessary variables
        self.load_config_file()

        # We get information from the screen

        root = tk.Tk()
        root.withdraw()
        self.horizontal = root.winfo_screenwidth()
        self.vertical = root.winfo_screenheight()
        root.destroy()

        print(f"Resolución de pantalla: {self.horizontal}x{self.vertical}")

        self.set_default_size(self.horizontal / 2, self.vertical)
        self.set_titlebar(header().get_new_header())

        main_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        menu_bar = Menu_bar(self)

        main_vertical_box.append(menu_bar.get_new_menu_bar())

        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        horizontal_box.set_vexpand(True)

        self.vertical_screen_1 = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_screen_1.set_hexpand(True)
        self.vertical_screen_1.set_vexpand(True)
        self.vertical_screen_2 = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.vertical_screen_2.set_hexpand(True)
        self.vertical_screen_2.set_vexpand(True)

        self.vertical_entry_1 = Gtk.Entry()
        self.vertical_entry_2 = Gtk.Entry()
        self.search_str_entry = Gtk.Entry()
        self.search_str_entry.set_editable(False)

        self.vertical_entry_1.set_focusable(False)
        self.vertical_entry_2.set_focusable(False)

        self.vertical_entry_1.set_margin_top(self.entry_margin)
        self.vertical_entry_1.set_margin_end(self.entry_margin / 2)
        self.vertical_entry_1.set_margin_bottom(self.entry_margin)
        self.vertical_entry_1.set_margin_start(self.entry_margin)
        self.vertical_entry_1.set_hexpand(True)

        self.vertical_entry_2.set_margin_top(self.entry_margin)
        self.vertical_entry_2.set_margin_end(self.entry_margin)
        self.vertical_entry_2.set_margin_bottom(self.entry_margin)
        self.vertical_entry_2.set_margin_start(self.entry_margin / 2)
        self.vertical_entry_2.set_hexpand(True)

        self.vertical_screen_1.append(self.vertical_entry_1)
        self.vertical_screen_2.append(self.vertical_entry_2)

        self.explorer_1 = Explorer(
            "explorer_1", self.vertical_entry_1, self, self.EXP_1_PATH
        )
        self.vertical_entry_1.set_text(str(self.explorer_1.actual_path))

        self.explorer_2 = Explorer(
            "explorer_2", self.vertical_entry_2, self, self.EXP_2_PATH
        )
        self.vertical_entry_2.set_text(str(self.explorer_2.actual_path))

        self.scroll_1 = Gtk.ScrolledWindow()
        self.scroll_1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_1.set_child(self.explorer_1)
        self.scroll_1.set_margin_end(self.scroll_1_margin / 2)
        self.scroll_1.set_margin_bottom(self.scroll_1_margin)
        self.scroll_1.set_margin_start(self.scroll_1_margin)

        self.scroll_2 = Gtk.ScrolledWindow()
        self.scroll_2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_2.set_child(self.explorer_2)
        self.scroll_2.set_margin_end(self.scroll_1_margin)
        self.scroll_2.set_margin_bottom(self.scroll_1_margin)
        self.scroll_2.set_margin_start(self.scroll_1_margin / 2)

        self.vertical_screen_1.append(self.scroll_1)
        self.vertical_screen_2.append(self.scroll_2)

        horizontal_box.append(self.vertical_screen_1)
        horizontal_box.append(self.vertical_screen_2)

        main_vertical_box.append(horizontal_box)

        horizontal_boton_menu = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_boton_menu.set_margin_top(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_end(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_bottom(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_start(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_hexpand(True)

        btn_F2 = Gtk.Button(label="Renombrar < F2 >")
        horizontal_boton_menu.append(btn_F2)

        btn_F5 = Gtk.Button(label="Copiar < F5 >")
        horizontal_boton_menu.append(btn_F5)

        btn_F6 = Gtk.Button(label="Mover < F6 >")
        horizontal_boton_menu.append(btn_F6)

        btn_F7 = Gtk.Button(label="Crear dir < F7 >")
        horizontal_boton_menu.append(btn_F7)

        btn_F8 = Gtk.Button(label="Eliminar < F8 >")
        horizontal_boton_menu.append(btn_F8)

        btn_F10 = Gtk.Button(label="Salir < F10 >")
        horizontal_boton_menu.append(btn_F10)

        horizontal_boton_menu.append(self.search_str_entry)

        horizontal_boton_menu.set_halign(Gtk.Align.CENTER)

        main_vertical_box.append(horizontal_boton_menu)

        self.set_child(main_vertical_box)

        # Signals and events area

        self.vertical_entry_1.connect(
            "activate", self.action.entry_change_path, self.explorer_1
        )
        self.vertical_entry_2.connect(
            "activate", self.action.entry_change_path, self.explorer_2
        )

        self.explorer_1.connect(
            "activate",
            self.action.on_doble_click_or_enter,
            self.explorer_1,
            self.vertical_entry_1,
        )
        self.explorer_2.connect(
            "activate",
            self.action.on_doble_click_or_enter,
            self.explorer_2,
            self.vertical_entry_2,
        )

        rename_logic = Rename_Logic()
        btn_F2.connect(
            "clicked",
            lambda btn: rename_logic.on_rename(self.explorer_src, self),
        )

        my_copy = My_copy()
        btn_F5.connect(
            "clicked",
            lambda btn: my_copy.on_copy(self.explorer_src, self.explorer_dst, self),
        )

        move = Move(self)
        btn_F6.connect(
            "clicked",
            lambda btn: move.on_move(self.explorer_src, self.explorer_dst),
        )

        create = Create()
        btn_F7.connect(
            "clicked",
            lambda btn: create.on_create_dir(
                self.explorer_src, self.explorer_dst, self
            ),
        )
        remove = Remove()
        btn_F8.connect(
            "clicked",
            lambda btn: remove.on_delete(self.explorer_src, self.explorer_dst, self),
        )

        btn_F10.connect(
            "clicked",
            lambda btn: self.exit(self),
        )

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect(
            "key-pressed", Action_keys.on_key_press, self, self.action
        )

        self.add_controller(key_controller)

        self.connect("close-request", self.exit)

    @staticmethod
    def get_windows():
        return self

    def set_explorer_focused(self, explorer_focused, explorer_unfocused):
        self.explorer_src = explorer_focused
        self.explorer_src.grab_focus()
        self.explorer_src.scroll_to(
            self.explorer_src.n_row, None, self.explorer_src.flags
        )
        self.explorer_dst = explorer_unfocused

    def exit(self, win=None):
        self.close()
        mwdog1 = self.explorer_1.get_watchdog()
        mwdog2 = self.explorer_2.get_watchdog()
        mwdog1.stop()
        mwdog2.stop()
        self.save_config_file()

    def set_explorer_initial(self):

        # LOAD DATA DIRECTORY
        self.explorer_1.load_new_path(self.explorer_1.actual_path)
        self.explorer_2.load_new_path(self.explorer_2.actual_path)

        # We set the initial focus to explorer_1, left
        self.action.set_explorer_to_focused(self.explorer_1, self)
        self.explorer_src = self.explorer_1
        self.explorer_dst = self.explorer_2

    def load_config_file(self):
        # If no configuration exists, it creates it, with default options
        if not self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, "a") as conf:
                conf.write("EXP_1_PATH=/\n")
                conf.write("EXP_2_PATH=/\n")

        # We open configuration and load in variables.
        with open(self.CONFIG_FILE, "r+") as conf:
            for row in conf:
                if row:
                    split = row.strip().split("=")
                    if split[0] == "EXP_1_PATH":
                        self.EXP_1_PATH = split[1]

                    if split[0] == "EXP_2_PATH":
                        self.EXP_2_PATH = split[1]

    def save_config_file(self):
        # Config is deleted and the entire configuration is saved.
        with open(self.CONFIG_FILE, "a") as conf:
            conf.seek(0)
            conf.truncate()
            conf.write(f"EXP_1_PATH={self.explorer_1.actual_path}\n")
            conf.write(f"EXP_2_PATH={self.explorer_2.actual_path}\n")
