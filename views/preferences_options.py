import gi


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402


class Preferences(Gtk.Window):

    GENERAL_LABEL_BTN = "General"
    DIRECTORY_LABEL_BTN = "Directorios"
    APPEARANCE_LABEL_BTN = "Apariencia"

    DIRECTORY_TITLE = "Directorios de inicio"
    UTILIZATION_LAST_DIR = "Utilizar últimos directorios usados."
    UTILIZATION_SET_DIR = "Utilizar siempre los mismos al iniciar."
    SELECT_FILE_TITLE = "Seleccionar archivo"
    LABEL_DIR_SELECT_LEFT = "Directorio izquierdo:"
    LABEL_DIR_SELECT_RIGHT = "Directorio derecho:"
    BTN_ACCEPT_LABEL = "Aceptar"
    BTN_CANCEL_LABEL = "Cancel"
    EXP_1_PATH = ""
    EXP_2_PATH = ""
    SHOW_DIR_LAST = None

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(title="Preferencias", transient_for=win)

        Preferences.SHOW_DIR_LAST = win.SHOW_DIR_LAST

        self.win = win
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
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
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
        self.destroy()

    def on_accept(self, button: Gtk.Button) -> None:
        """
        Confirm changes.
        """
        self.win.SHOW_DIR_LAST = Preferences.SHOW_DIR_LAST
        self.win.EXP_1_PATH = Preferences.EXP_1_PATH
        self.win.EXP_2_PATH = Preferences.EXP_2_PATH
        self.win.save_config_file()
        self.destroy()

    def create_general(self) -> None:
        """
        Create windows for general option
        """
        self.general_box.set_margin_top(20)
        self.general_box.set_margin_end(20)
        self.general_box.set_margin_bottom(20)
        self.general_box.set_margin_start(20)

        self.general_box.append(Gtk.Label(label="GENERAL"))

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

        dir_label_right = Gtk.Label(label=Preferences.LABEL_DIR_SELECT_RIGHT)
        dir_label_right.set_size_request(150, -1)

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
        # select_directory_box_1.set_halign(Gtk.Align.END)

        self.select_directory_box_2.append(dir_label_right)
        self.select_directory_box_2.append(entry_path_2)
        self.select_directory_box_2.append(sel_path_2_btn)
        # select_directory_box_2.set_halign(Gtk.Align.END)

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

        self.appearance_box.append(Gtk.Label(label="APPEARANCE"))

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
