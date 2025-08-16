from utilities.i18n import _
from css.explorer_css import Css_explorer_manager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GObject, Pango  # noqa: E402


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

    # Application colors

    BACKGROUND_APP_TITLE = _("Aplicación")
    BACKGROUND_APP_TITLE_COLOR = _("Fondo de la aplicación")

    # background entrys text

    BACKGROUND_ENTRY_TITLE = _("Entrada de ruta")
    BACKGROUND_ENTRY_TITLE_COLOR = _("Fondo de la entrada")

    # Background colors text
    BACKGROUND_EXPLORER_TITLE = _("Exploradores")
    BACKGROUND_EXPLORER_LEFT = _("Fondo explorador izquierdo")
    BACKGROUND_EXPLORER_RIGHT = _("Fondo explorador derecho")

    # Search colors text
    SEARCH_COLORS_TITLE = _("Colores del sistema de búsqueda")
    SEARCH_BACKGROUND = _("Color de fondo")
    SEARCH_FONT_COLOR = _("Color texto")

    # Buttons text
    BACKGROUND_BUTTONS_TITLE = _("Color de los botones")
    BACKGROUND_BUTTONS_LABEL = _("Fondo de los botones")

    # Font text

    FONT_SELECT_TITLE = _("Seleccion de fuente")
    FONT_SELECT_LABEL = _("Fuente")
    FONT_SELECT_COLOT = _("Color")

    # Colors

    COLOR_BACKGROUND_APP = None

    COLOR_ENTRY = None

    COLOR_EXPLORER_LEFT = None
    COLOR_EXPLORER_RIGHT = None

    COLOR_BACKGROUND_SEARCH = None
    COLOR_SEARCH_TEXT = None

    COLOR_BUTTON = None

    FONT_STYLE = None
    FONT_STYLE_COLOR = None

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(title=_("Preferencias"), transient_for=win)

        Preferences.SHOW_DIR_LAST = win.SHOW_DIR_LAST
        Preferences.SWITCH_IMG_STATUS = win.SWITCH_IMG_STATUS
        Preferences.COLOR_BACKGROUND_APP = win.COLOR_BACKGROUND_APP
        Preferences.COLOR_EXPLORER_LEFT = win.COLOR_EXPLORER_LEFT
        Preferences.COLOR_EXPLORER_RIGHT = win.COLOR_EXPLORER_RIGHT
        Preferences.COLOR_BACKGROUND_SEARCH = win.COLOR_BACKGROUND_SEARCH
        Preferences.COLOR_SEARCH_TEXT = win.COLOR_SEARCH_TEXT
        Preferences.FONT_STYLE = win.FONT_STYLE
        Preferences.FONT_STYLE_COLOR = win.FONT_STYLE_COLOR

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
        general_btn.get_style_context().add_class("button")
        general_btn.connect("clicked", self.change_box, self.general_box)
        directory_btn = Gtk.Button(label=Preferences.DIRECTORY_LABEL_BTN)
        directory_btn.get_style_context().add_class("button")
        directory_btn.connect("clicked", self.change_box, self.directory_box)
        appearance_btn = Gtk.Button(label=Preferences.APPEARANCE_LABEL_BTN)
        appearance_btn.get_style_context().add_class("button")
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
        self.horizontal_option_box.get_style_context().add_class(
            "border-style"
        )

        # box for accept or cancel buttons
        horizontal_option_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        horizontal_option_btn.set_hexpand(True)
        horizontal_option_btn.set_halign(Gtk.Align.END)

        btn_accept = Gtk.Button(label=Preferences.BTN_ACCEPT_LABEL)
        btn_accept.get_style_context().add_class("button")
        btn_accept.connect("clicked", self.on_accept)
        btn_cancel = Gtk.Button(label=Preferences.BTN_CANCEL_LABEL)
        btn_cancel.get_style_context().add_class("button")
        btn_cancel.connect("clicked", self.on_exit)

        horizontal_option_btn.append(btn_accept)
        horizontal_option_btn.append(btn_cancel)

        vertical_option_box.append(self.horizontal_option_box)
        vertical_option_box.append(horizontal_option_btn)

        horizontal_main.append(vertical_button_box)
        horizontal_main.append(vertical_option_box)

        self.present()

        self.change_box(Gtk.Button(), self.general_box)

        self.get_style_context().add_class("app_background")

        # Load css

        self.get_style_context().add_class("font-color")

    def on_exit(self, button: Gtk.Button) -> None:
        """
        Close preferencesc window
        """
        self.css_manager.load_css_app_background(self.win.COLOR_BACKGROUND_APP)
        self.css_manager.load_css_entrys(self.win.COLOR_ENTRY)
        self.css_manager.load_css_explorer_background(
            self.win.COLOR_EXPLORER_LEFT, self.win.COLOR_EXPLORER_RIGHT
        )
        self.css_manager.load_css_buttons(self.win.COLOR_BUTTON)
        font_desc = Pango.FontDescription.from_string(self.win.FONT_STYLE)
        self.css_manager.load_css_font(font_desc, Preferences.FONT_STYLE_COLOR)
        self.destroy()

    def on_accept(self, button: Gtk.Button) -> None:
        """
        Confirm changes.
        """
        self.win.SHOW_DIR_LAST = Preferences.SHOW_DIR_LAST
        self.win.EXP_1_PATH = Preferences.EXP_1_PATH
        self.win.EXP_2_PATH = Preferences.EXP_2_PATH
        self.win.SWITCH_IMG_STATUS = Preferences.SWITCH_IMG_STATUS
        self.win.COLOR_BACKGROUND_APP = Preferences.COLOR_BACKGROUND_APP
        self.win.COLOR_ENTRY = Preferences.COLOR_ENTRY
        self.win.COLOR_EXPLORER_LEFT = Preferences.COLOR_EXPLORER_LEFT
        self.win.COLOR_EXPLORER_RIGHT = Preferences.COLOR_EXPLORER_RIGHT
        self.win.COLOR_BUTTON = Preferences.COLOR_BUTTON
        self.win.COLOR_BACKGROUND_SEARCH = Preferences.COLOR_BACKGROUND_SEARCH
        self.win.COLOR_SEARCH_TEXT = Preferences.COLOR_SEARCH_TEXT
        self.win.FONT_STYLE = Preferences.FONT_STYLE
        self.win.FONT_STYLE_COLOR = Preferences.FONT_STYLE_COLOR

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

        # Background application

        self.background_horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.appearance_box.append(
            self.create_box_for_title_section(Preferences.BACKGROUND_APP_TITLE)
        )

        self.background_horizontal_box_app = self.create_box_for_color_btn()

        self.background_horizontal_box_app.append(
            self.create_label(Preferences.BACKGROUND_APP_TITLE_COLOR)
        )
        self.background_horizontal_box_app.append(
            self.create_btn_color("btn_color_app")
        )

        self.appearance_box.append(self.background_horizontal_box_app)

        # Background entrys

        self.appearance_box.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_ENTRY_TITLE
            )
        )

        self.background_horizontal_box_entry_color = (
            self.create_box_for_color_btn()
        )

        self.background_horizontal_box_entry_color.append(
            self.create_label(Preferences.BACKGROUND_ENTRY_TITLE_COLOR)
        )
        self.background_horizontal_box_entry_color.append(
            self.create_btn_color("btn_color_entry")
        )

        self.appearance_box.append(self.background_horizontal_box_entry_color)

        # Background explorers

        self.appearance_box.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_EXPLORER_TITLE
            )
        )

        self.background_horizontal_box_1 = self.create_box_for_color_btn()

        self.background_horizontal_box_1.append(
            self.create_label(Preferences.BACKGROUND_EXPLORER_LEFT)
        )
        self.background_horizontal_box_1.append(
            self.create_btn_color("btn_color_explorer_left")
        )

        self.appearance_box.append(self.background_horizontal_box_1)

        self.background_horizontal_box_2 = self.create_box_for_color_btn()

        self.background_horizontal_box_2.append(
            self.create_label(Preferences.BACKGROUND_EXPLORER_RIGHT)
        )
        self.background_horizontal_box_2.append(
            self.create_btn_color("btn_color_explorer_right")
        )

        self.appearance_box.append(self.background_horizontal_box_2)

        # Search section

        self.appearance_box.append(
            self.create_box_for_title_section(Preferences.SEARCH_COLORS_TITLE)
        )

        self.background_horizontal_box_3 = self.create_box_for_color_btn()

        self.background_horizontal_box_3.append(
            self.create_label(Preferences.SEARCH_BACKGROUND)
        )
        self.background_horizontal_box_3.append(
            self.create_btn_color("btn_color_background_search")
        )

        self.appearance_box.append(self.background_horizontal_box_3)

        self.background_horizontal_box_4 = self.create_box_for_color_btn()

        self.background_horizontal_box_4.append(
            self.create_label(Preferences.SEARCH_FONT_COLOR)
        )
        self.background_horizontal_box_4.append(
            self.create_btn_color("btn_color_search_text")
        )

        self.appearance_box.append(self.background_horizontal_box_4)

        # Set color button

        self.appearance_box.append(
            self.create_box_for_title_section(
                Preferences.BACKGROUND_BUTTONS_TITLE
            )
        )

        self.background_horizontal_box_4 = self.create_box_for_color_btn()

        self.background_horizontal_box_4.append(
            self.create_label(Preferences.BACKGROUND_BUTTONS_LABEL)
        )
        self.background_horizontal_box_4.append(
            self.create_btn_color("btn_color_background_buttons")
        )

        self.appearance_box.append(self.background_horizontal_box_4)

        # Font selector

        self.appearance_box.append(
            self.create_box_for_title_section(Preferences.FONT_SELECT_TITLE)
        )

        self.background_horizontal_box_font_btn = (
            self.create_box_for_color_btn()
        )

        font_dialog = Gtk.FontDialog.new()
        font_dialog.connect("notify::font-desc", self.set_font)
        btn_font = Gtk.FontDialogButton.new(font_dialog)
        font_desc = Pango.FontDescription.from_string(Preferences.FONT_STYLE)
        btn_font.set_font_desc(font_desc)
        btn_font.connect("notify::font-desc", self.set_font)

        self.background_horizontal_box_font_btn.append(
            self.create_label(Preferences.FONT_SELECT_LABEL)
        )
        self.background_horizontal_box_font_btn.append(btn_font)

        self.appearance_box.append(self.background_horizontal_box_font_btn)

        # Font color selector
        self.background_horizontal_box_font_color = (
            self.create_box_for_color_btn()
        )

        self.background_horizontal_box_font_color.append(
            self.create_label(Preferences.FONT_SELECT_COLOT)
        )
        self.background_horizontal_box_font_color.append(
            self.create_btn_color("btn_color_font_color")
        )

        self.appearance_box.append(self.background_horizontal_box_font_color)

    def set_font(
        self, button: Gtk.FontDialogButton, pspec: GObject.GParamSpec
    ) -> None:
        print("CAMBIOS")
        font_desc = button.get_font_desc()
        if font_desc:
            Preferences.FONT_STYLE = font_desc.to_string()
            self.css_manager.load_css_font(
                font_desc, Preferences.FONT_STYLE_COLOR
            )

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
        elif name == "btn_color_app":
            Preferences.COLOR_BACKGROUND_APP = color
            self.css_manager.load_css_app_background(
                Preferences.COLOR_BACKGROUND_APP
            )
        elif name == "btn_color_background_buttons":
            Preferences.COLOR_BUTTON = color
            self.css_manager.load_css_buttons(Preferences.COLOR_BUTTON)
        elif name == "btn_color_entry":
            Preferences.COLOR_ENTRY = color
            self.css_manager.load_css_entrys(Preferences.COLOR_ENTRY)
        elif name == "btn_color_font_color":
            Preferences.FONT_STYLE_COLOR = color
            font_desc = Pango.FontDescription.from_string(
                Preferences.FONT_STYLE
            )
            self.css_manager.load_css_font(
                font_desc, Preferences.FONT_STYLE_COLOR
            )

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
        elif name == "btn_color_app":
            Preferences.COLOR_BACKGROUND_APP = self.win.COLOR_BACKGROUND_APP
            color.parse(Preferences.COLOR_BACKGROUND_APP)
        elif name == "btn_color_background_buttons":
            Preferences.COLOR_BUTTON = self.win.COLOR_BUTTON
            color.parse(Preferences.COLOR_BUTTON)
        elif name == "btn_color_entry":
            Preferences.COLOR_ENTRY = self.win.COLOR_ENTRY
            color.parse(Preferences.COLOR_ENTRY)
        elif name == "btn_color_font_color":
            Preferences.FONT_STYLE_COLOR = self.win.FONT_STYLE_COLOR
            color.parse(Preferences.FONT_STYLE_COLOR)

        button.set_rgba(color)

    def create_box_for_title_section(self, text_label: str) -> Gtk.Box:
        """
        Create box and label for title section
        """
        box_for_title = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        label = Gtk.Label()
        label.set_markup(f"<u>{text_label}</u>")
        box_for_title.append(label)
        box_for_title.set_margin_top(40)

        return box_for_title

    def create_label(self, label_text: str) -> Gtk.Label:
        label = Gtk.Label(label=label_text)
        # label.set_margin_start(100)
        label.set_size_request(200, -1)
        label.set_xalign(0.0)
        return label

    def create_btn_color(self, btn_name: str) -> Gtk.ColorDialogButton:
        color_dialog = Gtk.ColorDialog()
        btn_color = Gtk.ColorDialogButton.new(color_dialog)
        btn_color.set_name(btn_name)
        btn_color.connect("notify::rgba", self.set_color)
        self.set_color_dialog_button(btn_color)
        return btn_color

    def create_box_for_color_btn(self) -> Gtk.Box:
        box_for_color_btn = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        box_for_color_btn.set_margin_start(100)
        return box_for_color_btn
