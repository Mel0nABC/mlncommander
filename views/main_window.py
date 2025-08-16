from utilities.i18n import _
from controls import Action_keys
from controls import Actions
from views.menu_bar import Menu_bar
from views.header import header
from views.explorer import Explorer
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.move import Move
from utilities.rename import Rename_Logic
from utilities.new_file import NewFile
from css.explorer_css import Css_explorer_manager
from pathlib import Path
import tkinter as tk
import os
import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango  # noqa E402


class Window(Gtk.ApplicationWindow):

    def __init__(self, app: Gtk.Application, action: Actions):
        super().__init__(application=app)

        # check app folder on user dir exist

        self.APP_USER_PATH = Path(f"{os.environ["HOME"]}/.mlncommander")

        username = os.getlogin()

        if username in str(self.APP_USER_PATH):
            if not self.APP_USER_PATH.exists():
                self.APP_USER_PATH.mkdir()
        self.app = app
        self.action = action
        self.key_controller_id = 0
        self.explorer_src = None
        self.explorer_dst = None
        self.my_watchdog = None
        self.entry_margin = 10
        self.horizontal_button_list_margin = 10
        self.scroll_margin = 10
        self.label_left_selected_files = None
        self.label_right_selected_files = None
        self.CONFIG_FILE = Path(f"{self.APP_USER_PATH}/config.conf")
        self.EXP_1_PATH = ""
        self.EXP_2_PATH = ""
        self.SHOW_DIR_LAST = True
        self.SWITCH_IMG_STATUS = None
        self.COLOR_BACKGROUND_APP = None
        self.COLOR_EXPLORER_LEFT = None
        self.COLOR_EXPLORER_RIGHT = None
        self.COLOR_BACKGROUND_SEARCH = None
        self.COLOR_ENTRY = None
        self.COLOR_SEARCH_TEXT = None
        self.COLOR_BUTTON = None
        self.FONT_STYLE = None

        # We load the configuration, to send necessary variables
        self.load_config_file()

        # Load css
        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.css_manager = Css_explorer_manager(self)
        self.css_manager.load_css_app_background(self.COLOR_BACKGROUND_APP)
        self.css_manager.load_css_buttons(self.COLOR_BUTTON)
        self.css_manager.load_css_entrys(self.COLOR_ENTRY)
        font_desc = Pango.FontDescription.from_string(self.FONT_STYLE)
        self.css_manager.load_css_font(font_desc)

        # We get information from the screen

        root = tk.Tk()
        root.withdraw()
        self.horizontal = root.winfo_screenwidth()
        self.vertical = root.winfo_screenheight()
        root.destroy()

        print(f"Screen resolution: {self.horizontal}x{self.vertical}")

        self.set_default_size(self.horizontal / 2, self.vertical)
        self.set_titlebar(header().header)

        main_vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        menu_bar = Menu_bar(self)

        main_vertical_box.append(menu_bar.menubar)

        horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
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
        self.vertical_entry_1.get_style_context().add_class("entry")
        self.vertical_entry_2 = Gtk.Entry()
        self.vertical_entry_2.get_style_context().add_class("entry")
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
            "explorer_1",
            self.vertical_entry_1,
            self,
            self.EXP_1_PATH,
            self.APP_USER_PATH,
        )
        self.vertical_entry_1.set_text(str(self.explorer_1.actual_path))

        self.explorer_2 = Explorer(
            "explorer_2",
            self.vertical_entry_2,
            self,
            self.EXP_2_PATH,
            self.APP_USER_PATH,
        )
        self.vertical_entry_2.set_text(str(self.explorer_2.actual_path))

        self.scroll_1 = Gtk.ScrolledWindow()
        self.scroll_1.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        self.scroll_1.set_child(self.explorer_1)
        self.scroll_1.set_margin_end(self.scroll_margin / 2)
        self.scroll_1.set_margin_start(self.scroll_margin)

        self.scroll_2 = Gtk.ScrolledWindow()
        self.scroll_2.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        self.scroll_2.set_child(self.explorer_2)
        self.scroll_2.set_margin_end(self.scroll_margin)
        self.scroll_2.set_margin_start(self.scroll_margin / 2)

        self.vertical_screen_1.append(self.scroll_1)
        self.vertical_screen_2.append(self.scroll_2)

        horizontal_box.append(self.vertical_screen_1)
        horizontal_box.append(self.vertical_screen_2)

        main_vertical_box.append(horizontal_box)

        horizontal_botton_menu = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_botton_menu.set_margin_top(
            self.horizontal_button_list_margin
        )
        horizontal_botton_menu.set_margin_end(
            self.horizontal_button_list_margin
        )
        horizontal_botton_menu.set_margin_bottom(
            self.horizontal_button_list_margin
        )
        horizontal_botton_menu.set_margin_start(
            self.horizontal_button_list_margin
        )
        horizontal_botton_menu.set_hexpand(True)

        btn_F2 = Gtk.Button(label=_("Renombrar < F2 >"))
        btn_F2.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F2)

        btn_F3 = Gtk.Button(label=_("Nuevo Fichero < F3 >"))
        btn_F3.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F3)

        btn_F5 = Gtk.Button(label=_("Copiar < F5 >"))
        btn_F5.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F5)

        btn_F6 = Gtk.Button(label=_("Mover < F6 >"))
        btn_F6.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F6)

        btn_F7 = Gtk.Button(label=_("Crear dir < F7 >"))
        btn_F7.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F7)

        btn_F8 = Gtk.Button(label=_("Eliminar < F8 >"))
        btn_F8.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F8)

        btn_F9 = Gtk.Button(label=_("Duplicar < F9 >"))
        btn_F9.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F9)

        btn_F10 = Gtk.Button(label=_("Salir < F10 >"))
        btn_F10.get_style_context().add_class("button")
        horizontal_botton_menu.append(btn_F10)

        # Left label show selection info
        label_box_left = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.label_left_selected_files = Gtk.Label(label="--")
        label_box_left.set_hexpand(True)
        label_box_left.append(self.label_left_selected_files)

        # Right label show selection info
        label_box_right = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.label_right_selected_files = Gtk.Label(label="--")

        label_box_right.set_hexpand(True)
        label_box_right.append(self.label_right_selected_files)

        label_box_right.set_halign(Gtk.Align.END)

        horizontal_botton_menu.set_halign(Gtk.Align.CENTER)

        horizontal_bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_bottom.append(label_box_left)
        horizontal_bottom.append(horizontal_botton_menu)
        horizontal_bottom.append(label_box_right)

        horizontal_bottom.set_hexpand(True)
        horizontal_bottom.set_margin_start(self.scroll_margin + 20)
        horizontal_bottom.set_margin_end(self.scroll_margin + 20)

        main_vertical_box.append(horizontal_bottom)

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

        new_file = NewFile()
        btn_F3.connect(
            "clicked",
            lambda btn: new_file.on_new_file(self.explorer_src, self),
        )

        my_copy = My_copy()
        btn_F5.connect(
            "clicked",
            lambda btn: my_copy.on_copy(
                self.explorer_src, self.explorer_dst, None, self
            ),
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
            lambda btn: remove.on_delete(
                self.explorer_src, self.explorer_dst, self
            ),
        )

        my_copy = My_copy()
        btn_F9.connect(
            "clicked",
            lambda btn: my_copy.on_duplicate(
                self.explorer_src, self.explorer_dst, self
            ),
        )

        btn_F10.connect(
            "clicked",
            lambda btn: self.exit(self),
        )

        # Event controller to control keys
        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller_id = self.key_controller.connect(
            "key-pressed", Action_keys.on_key_press, self, self.action
        )
        self.add_controller(self.key_controller)
        self.connect("close-request", self.exit)

    def set_explorer_focused(
        self, explorer_focused: Explorer, explorer_unfocused: Explorer
    ) -> None:
        """
        Set focus on explorer
        """
        self.explorer_src = explorer_focused
        self.explorer_src.grab_focus()
        self.explorer_src.scroll_to(
            self.explorer_src.n_row, None, self.explorer_src.flags
        )
        self.explorer_dst = explorer_unfocused

    def exit(self, win: Gtk.ApplicationWindow = None) -> None:
        """
        Close services, save configuration and close application
        """
        self.close()
        self.explorer_1.my_watchdog.stop()
        self.explorer_2.my_watchdog.stop()
        self.save_config_file()

    def set_explorer_initial(self) -> None:
        """
        Set browser 1 (left) as default when starting the application
        """
        # LOAD DATA DIRECTORY
        self.explorer_1.load_new_path(self.explorer_1.actual_path)
        self.explorer_2.load_new_path(self.explorer_2.actual_path)

        # We set the initial focus to explorer_1, left
        self.action.set_explorer_to_focused(self.explorer_1, self)
        self.explorer_src = self.explorer_1
        self.explorer_dst = self.explorer_2

    def load_config_file(self) -> None:
        """
        load config file
        """

        # If no configuration exists, it creates it, with default options
        if not self.CONFIG_FILE.exists():
            app_background_prede = "#353535"
            explorer_background_prede = "#222226"
            with open(self.CONFIG_FILE, "a") as conf:
                conf.write("EXP_1_PATH=/\n")
                conf.write("EXP_2_PATH=/\n")
                conf.write("SHOW_DIR_LAST=True\n")
                conf.write("SWITCH_IMG_STATUS=True\n")

                conf.write(f"COLOR_BACKGROUND_APP={app_background_prede}\n")
                conf.write("COLOR_ENTRY=#2d2d2d\n")
                conf.write(
                    f"COLOR_EXPLORER_LEFT={explorer_background_prede}\n"
                )
                conf.write(
                    f"COLOR_EXPLORER_RIGHT={explorer_background_prede}\n"
                )
                conf.write("COLOR_BUTTON=#393939\n")
                conf.write("COLOR_BACKGROUND_SEARCH=rgb(0,0,0)\n")
                conf.write("COLOR_SEARCH_TEXT=rgb(246,211,45)\n")
                conf.write("FONT_STYLE=Adwaita Mono 12\n")

        # We open configuration and load in variables.
        with open(self.CONFIG_FILE, "r+") as conf:
            for row in conf:
                if row:
                    split = row.strip().split("=")
                    result = ""
                    variable_name = split[0]
                    if (
                        variable_name == "EXP_1_PATH"
                        or variable_name == "EXP_2_PATH"
                    ):
                        path = Path(split[1])
                        if path.exists():
                            setattr(self, variable_name, path)
                        else:
                            setattr(self, variable_name, "/")

                    elif variable_name == "SHOW_DIR_LAST":
                        result = True if split[1] == "True" else False
                        setattr(self, variable_name, result)
                    elif variable_name == "SWITCH_IMG_STATUS":
                        result = True if split[1] == "True" else False
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_ENTRY":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_EXPLORER_LEFT":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_EXPLORER_RIGHT":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_BUTTON":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_BACKGROUND_SEARCH":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_SEARCH_TEXT":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "COLOR_BACKGROUND_APP":
                        result = split[1]
                        setattr(self, variable_name, result)
                    elif variable_name == "FONT_STYLE":
                        result = split[1]
                        setattr(self, variable_name, result)

    def save_config_file(self) -> None:
        """
        Saves the settings to the current location
        where the browsers are located
        """
        # Config is deleted and the entire configuration is saved.
        with open(self.CONFIG_FILE, "a") as conf:
            conf.seek(0)
            conf.truncate()
            if self.SHOW_DIR_LAST:
                conf.write(f"EXP_1_PATH={self.explorer_1.actual_path}\n")
                conf.write(f"EXP_2_PATH={self.explorer_2.actual_path}\n")
            else:
                conf.write(f"EXP_1_PATH={self.EXP_1_PATH}\n")
                conf.write(f"EXP_2_PATH={self.EXP_2_PATH}\n")

            conf.write(f"SHOW_DIR_LAST={self.SHOW_DIR_LAST}\n")
            conf.write(f"SWITCH_IMG_STATUS={self.SWITCH_IMG_STATUS}\n")
            conf.write(f"COLOR_BACKGROUND_APP={self.COLOR_BACKGROUND_APP}\n")
            conf.write(f"COLOR_ENTRY={self.COLOR_ENTRY}\n")
            conf.write(f"COLOR_EXPLORER_LEFT={self.COLOR_EXPLORER_LEFT}\n")
            conf.write(f"COLOR_EXPLORER_RIGHT={self.COLOR_EXPLORER_RIGHT}\n")
            conf.write(f"COLOR_BUTTON={self.COLOR_BUTTON}\n")
            conf.write(
                f"COLOR_BACKGROUND_SEARCH={self.COLOR_BACKGROUND_SEARCH}\n"
            )
            conf.write(f"COLOR_SEARCH_TEXT={self.COLOR_SEARCH_TEXT}\n")
            conf.write(f"FONT_STYLE={self.FONT_STYLE}\n")

    def get_other_explorer_with_name(self, name: str) -> Explorer:
        """
        Returns the browser that does not contain the passed name
        """
        for explorer in [self.explorer_1, self.explorer_2]:
            if explorer.name != name:
                return explorer

        return None
