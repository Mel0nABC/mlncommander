from utilities.i18n import _
import gi

from css.explorer_css import Css_explorer_manager

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GObject  # noqa: E402


class Preferences(Gtk.Window):

    GENERAL_LABEL_BTN = _("General")
    DIRECTORY_LABEL_BTN = _("Directorios")
    APPEARANCE_LABEL_BTN = _("Apariencia")

    DIRECTORY_TITLE = _("Directorios de inicio")
    UTILIZATION_LAST_DIR = _("Utilizar últimos directorios usados.")
    UTILIZATION_SET_DIR = _("Utilizar siempre los mismos al iniciar.")
    SELECT_FILE_TITLE = _("Seleccionar archivo")
    LABEL_DIR_SELECT_LEFT = _("Directorio izquierdo:")
    LABEL_DIR_SELECT_RIGHT = _("Directorio derecho:")
    BTN_ACCEPT_LABEL = _("Aceptar")
    BTN_CANCEL_LABEL = _("Cancel")
    EXP_1_PATH = ""
    EXP_2_PATH = ""
    SHOW_DIR_LAST = None
    SHOW_IMAGE_PREVIEW_LABEL = _(
        "Mostrar preview de la imagen al seleccionar:"
    )
    SWITCH_IMG_STATUS = None

    APARENCE_TITLE_COLOR = _("Colores")

    # Background colors text
    BACKGROUND_EXPLORER_LEFT = _("Fondo explorador izquierdo:")
    BACKGROUND_EXPLORER_RIGHT = _("Fondo explorador derecho:")

    # Search colors text
    SEARCH_COLORS_TITLE = _("Colores del sistema de búsqueda")
    SEARCH_BACKGROUND = _("Color de fondo:")
    SEARCH_FONT_COLOR = _("Color texto:")

    # Colors
    COLOR_EXPLORER_LEFT = None
    COLOR_EXPLORER_RIGHT = None
    COLOR_BACKGROUND_SEARCH = None
    COLOR_SEARCH_TEXT = None

    FONT_SIZE_EXPLORER = None
    FONT_BOLD_EXPLORER = None

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(title=_("Preferencias"), transient_for=win)

        Preferences.SHOW_DIR_LAST = win.SHOW_DIR_LAST
        Preferences.SWITCH_IMG_STATUS = win.SWITCH_IMG_STATUS
        Preferences.COLOR_EXPLORER_LEFT = win.COLOR_EXPLORER_LEFT
        Preferences.COLOR_EXPLORER_RIGHT = win.COLOR_EXPLORER_RIGHT
        Preferences.COLOR_BACKGROUND_SEARCH = win.COLOR_BACKGROUND_SEARCH
        Preferences.COLOR_SEARCH_TEXT = win.COLOR_SEARCH_TEXT
        Preferences.FONT_SIZE_EXPLORER = win.FONT_SIZE_EXPLORER
        Preferences.FONT_BOLD_EXPLORER = win.FONT_BOLD_EXPLORER

        self.win = win
        self.css_manager = Css_explorer_manager(self.win)
        self.select_directory_box_1 = None
        self.select_directory_box_2 = None

        # Creating option screens

        self.general_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.general_box.set_name("general_box")
        self.create_general()

        self.directory_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.directory_box.set_name("directory_box")
        self.create_directory()

        self.appearance_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        self.appearance_box.set_name("appearance_box")
        self.appearance_box.set_halign(Gtk.Align.START)
        self.create_appearance()

        self.set_default_size(900, 700)

        # Contain vertical button box and main option screen
        horizontal_main = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_main.set_margin_top(20)
        horizontal_main.set_margin_end(20)
        horizontal_main.set_margin_bottom(20)
        horizontal_main.set_margin_start(20)

        self.set_child(horizontal_main)

        # Box for buttons
        vertical_button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_button_box.set_vexpand(True)

        general_btn = Gtk.Button(label=Preferences.GENERAL_LABEL_BTN)
        general_btn.connect("clicked", self.change_box, self.general_box)
        directory_btn = Gtk.Button(label=Preferences.DIRECTORY_LABEL_BTN)
        directory_btn.connect("clicked", self.change_box, self.directory_box)
        appearance_btn = Gtk.Button(label=Preferences.APPEARANCE_LABEL_BTN)
        appearance_btn.connect("clicked", self.change_box, self.appearance_box)

        vertical_button_box.append(general_btn)
        vertical_button_box.append(directory_btn)
        vertical_button_box.append(appearance_btn)

        # Contain buttons for accept or cancel
        vertical_option_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_option_box.set_vexpand(True)

        # Where the multiple screens are displayed
        self.horizontal_option_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        self.horizontal_option_box.set_hexpand(True)
        self.horizontal_option_box.set_vexpand(True)

        # box for accept or cancel buttons
        horizontal_option_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_option_btn.set_hexpand(True)
        horizontal_option_btn.set_halign(Gtk.Align.END)

        btn_accept = Gtk.Button(label=Preferences.BTN_ACCEPT_LABEL)
        btn_accept.connect("clicked", self.on_accept)
        btn_cancel = Gtk.Button(label=Preferences.BTN_CANCEL_LABEL)
        btn_cancel.connect("clicked", self.on_exit)

        horizontal_option_btn.append(btn_accept)
        horizontal_option_btn.append(btn_cancel)

        vertical_option_box.append(self.horizontal_option_box)
        vertical_option_box.append(horizontal_option_btn)

        horizontal_main.append(vertical_button_box)
        horizontal_main.append(vertical_option_box)

        self.present()

        self.change_box(Gtk.Button(), self.general_box)

    def on_exit(self, button: Gtk.Button) -> None:
        """
        Close preferencesc window
        """
        self.css_manager.load_css_explorer_background(
            self.win.COLOR_EXPLORER_LEFT, self.win.COLOR_EXPLORER_RIGHT
        )
        self.destroy()

    def on_accept(self, button: Gtk.Button) -> None:
        """
        Confirm changes.
        """
        self.win.SHOW_DIR_LAST = Preferences.SHOW_DIR_LAST
        self.win.EXP_1_PATH = Preferences.EXP_1_PATH
        self.win.EXP_2_PATH = Preferences.EXP_2_PATH
        self.win.SWITCH_IMG_STATUS = Preferences.SWITCH_IMG_STATUS
        self.win.COLOR_EXPLORER_LEFT = Preferences.COLOR_EXPLORER_LEFT
        self.win.COLOR_EXPLORER_RIGHT = Preferences.COLOR_EXPLORER_RIGHT
        self.win.COLOR_BACKGROUND_SEARCH = Preferences.COLOR_BACKGROUND_SEARCH
        self.win.COLOR_SEARCH_TEXT = Preferences.COLOR_SEARCH_TEXT

        self.win.save_config_file()
        self.destroy()

    def change_box(self, button: Gtk.Button, actual_box: Gtk.Box) -> None:
        """
        Method to change visible option
        """

        old_child = self.horizontal_option_box.get_first_child()

        if old_child:

            if old_child.get_name() == actual_box.get_name():
                return

            self.horizontal_option_box.remove(old_child)

        self.horizontal_option_box.append(actual_box)

    def create_general(self) -> None:
        """
        Create windows for general option
        """
        self.general_box.set_margin_top(20)
        self.general_box.set_margin_end(20)
        self.general_box.set_margin_bottom(20)
        self.general_box.set_margin_start(20)

        self.general_box.append(Gtk.Label(label=_("GENERAL")))

    def create_directory(self) -> None:
        """
        Create windows for directory option
        """
        self.directory_box.set_margin_top(20)
        self.directory_box.set_margin_end(20)
        self.directory_box.set_margin_bottom(20)
        self.directory_box.set_margin_start(20)

        # title
        label_title = Gtk.Label(label=Preferences.DIRECTORY_TITLE)
        label_title.set_halign(Gtk.Align.START)

        # Buttons to select the option to use in directories
        check_button_last_dir = Gtk.CheckButton.new_with_label(
            Preferences.UTILIZATION_LAST_DIR
        )
        check_button_last_dir.set_halign(Gtk.Align.START)

        check_button_set_dir = Gtk.CheckButton.new_with_label(
            Preferences.UTILIZATION_SET_DIR
        )
        check_button_set_dir.set_halign(Gtk.Align.START)

        check_button_set_dir.set_group(check_button_last_dir)

        self.directory_box.append(label_title)
        self.directory_box.append(check_button_last_dir)
        self.directory_box.append(check_button_set_dir)

        # Select directorys to show

        self.select_directory_box_1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.select_directory_box_2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        dir_label_left = Gtk.Label(label=Preferences.LABEL_DIR_SELECT_LEFT)
        dir_label_left.set_size_request(150, -1)
        dir_label_left.set_xalign(0.0)

        dir_label_right = Gtk.Label(label=Preferences.LABEL_DIR_SELECT_RIGHT)
        dir_label_right.set_size_request(150, -1)
        dir_label_right.set_xalign(0.0)

        entry_path_1 = Gtk.Entry()
        entry_path_1.set_hexpand(True)
        entry_path_1.set_margin_start(40)
        entry_path_1.set_editable(False)
        entry_path_1.set_sensitive(False)
        Preferences.EXP_1_PATH = self.win.EXP_1_PATH
        entry_path_1.set_text(str(Preferences.EXP_1_PATH))
        entry_path_1.set_name("path_1")

        entry_path_2 = Gtk.Entry()
        entry_path_2.set_hexpand(True)
        entry_path_2.set_margin_start(40)
        entry_path_2.set_editable(False)
        entry_path_2.set_sensitive(False)
        Preferences.EXP_2_PATH = self.win.EXP_2_PATH
        entry_path_2.set_text(str(Preferences.EXP_2_PATH))
        entry_path_2.set_name("path_2")

        sel_path_1_btn = Gtk.Button(label="...")
        sel_path_1_btn.connect(
            "clicked", self.click_select_path_dialog, entry_path_1
        )

        sel_path_2_btn = Gtk.Button(label="...")
        sel_path_2_btn.connect(
            "clicked", self.click_select_path_dialog, entry_path_2
        )

        self.select_directory_box_1.append(dir_label_left)
        self.select_directory_box_1.append(entry_path_1)
        self.select_directory_box_1.append(sel_path_1_btn)

        self.select_directory_box_2.append(dir_label_right)
        self.select_directory_box_2.append(entry_path_2)
        self.select_directory_box_2.append(sel_path_2_btn)

        self.directory_box.append(self.select_directory_box_1)
        self.directory_box.append(self.select_directory_box_2)

        # Signals for check buttons

        check_button_last_dir.connect(
            "toggled", self.directory_select_option_last_dir
        )
        check_button_set_dir.connect(
            "toggled",
            self.directory_select_option_set_dir,
            entry_path_1,
            entry_path_2,
        )

        if Preferences.SHOW_DIR_LAST:
            check_button_last_dir.set_active(True)
        else:
            check_button_set_dir.set_active(True)

        img_preview_label = Gtk.Label(
            label=Preferences.SHOW_IMAGE_PREVIEW_LABEL
        )

        image_preview_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        image_preview_box.set_margin_top(20)
        image_preview_box.append(img_preview_label)

        switch_img = Gtk.Switch.new()
        switch_img.set_active(Preferences.SWITCH_IMG_STATUS)
        switch_img.connect("state-set", self.on_press_switch)

        image_preview_box.append(switch_img)
        self.directory_box.append(image_preview_box)

    def on_press_switch(self, switch: Gtk.Switch, pspec: bool) -> None:
        """
        When change switch status, update visual on explorers
        """
        Preferences.SWITCH_IMG_STATUS = pspec
        self.win.SWITCH_IMG_STATUS = pspec

        explorer_1 = self.win.explorer_1
        explorer_2 = self.win.explorer_2

        if explorer_1.focused:
            index = explorer_1.get_selected_items_from_explorer()[0]
            explorer_1.scroll_to(0, None, explorer_1.flags)
            explorer_1.scroll_to(index, None, explorer_1.flags)

        if explorer_2.focused:
            index = explorer_2.get_selected_items_from_explorer()[0]
            explorer_2.scroll_to(0, None, explorer_1.flags)
            explorer_2.scroll_to(index, None, explorer_1.flags)

    def click_select_path_dialog(
        self, button: Gtk.Button, entry: Gtk.Entry
    ) -> None:
        """
        Generate FileDialog to select folder
        """
        file_dialog = Gtk.FileDialog(title=Preferences.SELECT_FILE_TITLE)
        file_dialog.select_folder(self, None, self.on_file_selected, entry)

    def on_file_selected(
        self, dialog: Gtk.FileDialog, result: Gio.Task, entry: Gtk.Entry
    ) -> None:
        folder = dialog.select_folder_finish(result)
        if folder:
            if isinstance(entry, Gtk.Entry):
                value = folder.get_path()
                entry.set_text(value)
                if entry.get_name() == "path_1":
                    Preferences.EXP_1_PATH = value
                else:
                    Preferences.EXP_2_PATH = value

    def directory_select_option_last_dir(self, button: Gtk.Button) -> None:
        """
        Change on gui to select last dir option
        """
        self.select_directory_box_1.set_sensitive(False)
        self.select_directory_box_2.set_sensitive(False)
        Preferences.SHOW_DIR_LAST = True

    def directory_select_option_set_dir(
        self, button: Gtk.Button, entry_1: Gtk.Entry, entry_2: Gtk.Entry
    ) -> None:
        """
        Change on gui to select set dir option
        """
        self.select_directory_box_1.set_sensitive(True)
        self.select_directory_box_2.set_sensitive(True)
        Preferences.SHOW_DIR_LAST = False
        self.win.EXP_1_PATH = entry_1.get_text()
        self.win.EXP_2_PATH = entry_2.get_text()

    def create_appearance(self) -> None:
        """
        Create windows for appearance option
        """
        self.appearance_box.set_margin_top(20)
        self.appearance_box.set_margin_end(20)
        self.appearance_box.set_margin_bottom(20)
        self.appearance_box.set_margin_start(20)

        # Background explorers

        self.background_horizontal_box_0 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.background_horizontal_box_0.append(
            Gtk.Label(label=Preferences.APARENCE_TITLE_COLOR)
        )

        self.appearance_box.append(self.background_horizontal_box_0)

        self.background_horizontal_box_1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.background_horizontal_box_1.set_margin_top(20)

        label_explorer_back_left = Gtk.Label(
            label=Preferences.BACKGROUND_EXPLORER_LEFT
        )
        label_explorer_back_left.set_margin_start(100)
        label_explorer_back_left.set_size_request(200, -1)
        label_explorer_back_left.set_xalign(0.0)

        color_dialog = Gtk.ColorDialog()
        btn_color_explorer_left = Gtk.ColorDialogButton.new(color_dialog)
        btn_color_explorer_left.set_name("btn_color_explorer_left")
        btn_color_explorer_left.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color_explorer_left)

        self.background_horizontal_box_1.append(label_explorer_back_left)
        self.background_horizontal_box_1.append(btn_color_explorer_left)

        self.background_horizontal_box_2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.background_horizontal_box_2.set_margin_top(20)

        label_explorer_back_right = Gtk.Label(
            label=Preferences.BACKGROUND_EXPLORER_RIGHT
        )
        label_explorer_back_right.set_margin_start(100)
        label_explorer_back_right.set_size_request(200, -1)
        label_explorer_back_right.set_xalign(0.0)

        btn_color_explorer_right = Gtk.ColorDialogButton.new(color_dialog)
        btn_color_explorer_right.set_name("btn_color_explorer_right")
        btn_color_explorer_right.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color_explorer_right)

        self.background_horizontal_box_2.append(label_explorer_back_right)
        self.background_horizontal_box_2.append(btn_color_explorer_right)

        self.appearance_box.append(self.background_horizontal_box_1)
        self.appearance_box.append(self.background_horizontal_box_2)

        # Search colors

        label_search_colors_title = Gtk.Label(
            label=Preferences.SEARCH_COLORS_TITLE
        )
        label_search_colors_title.set_halign(Gtk.Align.START)
        label_search_colors_title.set_margin_top(20)

        self.appearance_box.append(label_search_colors_title)

        self.background_horizontal_box_3 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.background_horizontal_box_3.set_margin_top(20)

        btn_color_background_search = Gtk.ColorDialogButton.new(color_dialog)
        btn_color_background_search.set_name("btn_color_background_search")
        btn_color_background_search.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color_background_search)

        label_search_background = Gtk.Label(
            label=Preferences.SEARCH_BACKGROUND
        )
        label_search_background.set_margin_start(100)
        label_search_background.set_size_request(200, -1)
        label_search_background.set_xalign(0.0)

        self.background_horizontal_box_3.append(label_search_background)
        self.background_horizontal_box_3.append(btn_color_background_search)

        self.background_horizontal_box_4 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.background_horizontal_box_4.set_margin_top(20)

        label_search_font = Gtk.Label(label=Preferences.SEARCH_FONT_COLOR)
        label_search_font.set_margin_start(100)
        label_search_font.set_size_request(200, -1)
        label_search_font.set_xalign(0.0)

        btn_color_search_text = Gtk.ColorDialogButton.new(color_dialog)
        btn_color_search_text.set_name("btn_color_search_text")
        btn_color_search_text.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color_search_text)

        self.background_horizontal_box_4.append(label_search_font)
        self.background_horizontal_box_4.append(btn_color_search_text)

        self.appearance_box.append(self.background_horizontal_box_3)
        self.appearance_box.append(self.background_horizontal_box_4)
        self.background_horizontal_box_3.set_halign(Gtk.Align.END)
        self.background_horizontal_box_4.set_halign(Gtk.Align.END)

    def set_color(
        self, button: Gtk.ColorButton, pspec: GObject.GParamSpec
    ) -> None:
        color = button.get_rgba().to_string()
        name = button.get_name()

        if name == "btn_color_explorer_left":
            Preferences.COLOR_EXPLORER_LEFT = color
        elif name == "btn_color_explorer_right":
            Preferences.COLOR_EXPLORER_RIGHT = color
        elif name == "btn_color_background_search":
            Preferences.COLOR_BACKGROUND_SEARCH = color
        elif name == "btn_color_search_text":
            Preferences.COLOR_SEARCH_TEXT = color

        self.css_manager.load_css_explorer_background(
            Preferences.COLOR_EXPLORER_LEFT, Preferences.COLOR_EXPLORER_RIGHT
        )

    def set_color_dialog_button(self, button: Gtk.ColorDialogButton) -> None:
        color = Gdk.RGBA()
        name = button.get_name()
        if name == "btn_color_explorer_left":
            Preferences.COLOR_EXPLORER_LEFT = self.win.COLOR_EXPLORER_LEFT
            color.parse(Preferences.COLOR_EXPLORER_LEFT)
        elif name == "btn_color_explorer_right":
            Preferences.COLOR_EXPLORER_RIGHT = self.win.COLOR_EXPLORER_RIGHT
            color.parse(Preferences.COLOR_EXPLORER_RIGHT)
        elif name == "btn_color_background_search":
            Preferences.COLOR_BACKGROUND_SEARCH = (
                self.win.COLOR_BACKGROUND_SEARCH
            )
            color.parse(Preferences.COLOR_BACKGROUND_SEARCH)
        elif name == "btn_color_search_text":
            Preferences.COLOR_SEARCH_TEXT = self.win.COLOR_SEARCH_TEXT
            color.parse(Preferences.COLOR_SEARCH_TEXT)

        button.set_rgba(color)
