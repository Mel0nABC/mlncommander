# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402


class Directory(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow, parent: Gtk.Window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # DIRECTORYS

        self.DIRECTORY_TITLE = _("Directorios de inicio")
        self.UTILIZATION_LAST_DIR = _("Utilizar últimos directorios usados.")
        self.UTILIZATION_SET_DIR = _("Utilizar siempre los mismos al iniciar.")
        self.SELECT_FILE_TITLE = _("Seleccionar archivo")
        self.LABEL_DIR_SELECT_LEFT = _("Directorio izquierdo:")
        self.LABEL_DIR_SELECT_RIGHT = _("Directorio derecho:")
        self.BTN_RST_LABEL = _("Resetear")
        self.BTN_ACCEPT_LABEL = _("Aceptar")
        self.BTN_CANCEL_LABEL = _("Cancel")
        self.EXP_1_PATH = ""
        self.EXP_2_PATH = ""
        self.SHOW_IMAGE_PREVIEW_LABEL = _(
            "Mostrar preview de la imagen al seleccionar:"
        )
        self.SHOW_WATCHDOG_PREVIEW_LABEL = _("Activar o desactivar watchdog:")
        self.TERMINAL_EXECUTABLE_LABEL = _(
            "Indica el comando para abrir la termianl\n"
            "y la flag del directorio de trabajo\n"
            "Ejemplo: --workdir, --working-directory, etc"
        )

        self.SHOW_DIR_LAST = win.config.SHOW_DIR_LAST
        self.SWITCH_IMG_STATUS = win.config.SWITCH_IMG_STATUS
        self.SWITCH_WATCHDOG_STATUS = win.config.SWITCH_WATCHDOG_STATUS
        self.TERMINAL_COMMAND = win.config.TERMINAL_COMMAND

        self.win = win
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        # title
        title_label = Gtk.Label(label=self.DIRECTORY_TITLE)
        title_label.set_halign(Gtk.Align.START)

        # Buttons to select the option to use in directories
        check_button_last_dir = Gtk.CheckButton.new_with_label(
            self.UTILIZATION_LAST_DIR
        )
        check_button_last_dir.set_halign(Gtk.Align.START)

        check_button_set_dir = Gtk.CheckButton.new_with_label(
            self.UTILIZATION_SET_DIR
        )
        check_button_set_dir.set_halign(Gtk.Align.START)

        check_button_set_dir.set_group(check_button_last_dir)

        self.append(title_label)
        self.append(check_button_last_dir)
        self.append(check_button_set_dir)

        # Select directorys to show

        self.select_directory_box_1 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        self.select_directory_box_2 = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        dir_label_left = Gtk.Label(label=self.LABEL_DIR_SELECT_LEFT)
        dir_label_left.set_size_request(150, -1)
        dir_label_left.set_xalign(0.0)

        dir_label_right = Gtk.Label(label=self.LABEL_DIR_SELECT_RIGHT)
        dir_label_right.set_size_request(150, -1)
        dir_label_right.set_xalign(0.0)

        entry_path_1 = Gtk.Entry()
        entry_path_1.set_hexpand(True)
        entry_path_1.set_margin_start(40)
        entry_path_1.set_editable(False)
        entry_path_1.set_sensitive(False)
        self.EXP_1_PATH = self.win.config.EXP_1_PATH
        entry_path_1.set_text(str(self.EXP_1_PATH))
        entry_path_1.set_name("path_1")

        entry_path_2 = Gtk.Entry()
        entry_path_2.set_hexpand(True)
        entry_path_2.set_margin_start(40)
        entry_path_2.set_editable(False)
        entry_path_2.set_sensitive(False)
        self.EXP_2_PATH = self.win.config.EXP_2_PATH
        entry_path_2.set_text(str(self.EXP_2_PATH))
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

        self.append(self.select_directory_box_1)
        self.append(self.select_directory_box_2)

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

        if self.SHOW_DIR_LAST:
            check_button_last_dir.set_active(True)
        else:
            check_button_set_dir.set_active(True)

        # Image preview

        img_preview_label = Gtk.Label(label=self.SHOW_IMAGE_PREVIEW_LABEL)
        img_preview_label.set_halign(Gtk.Align.START)
        switch_img = Gtk.Switch.new()
        switch_img.set_halign(Gtk.Align.END)
        switch_img.set_active(self.SWITCH_IMG_STATUS)
        switch_img.connect("state-set", self.on_press_switch_img)

        # Watchdog on/off

        watchdog_label = Gtk.Label(label=self.SHOW_WATCHDOG_PREVIEW_LABEL)
        watchdog_label.set_halign(Gtk.Align.START)
        sw_watchdog = Gtk.Switch.new()
        sw_watchdog.set_halign(Gtk.Align.END)
        sw_watchdog.set_active(self.SWITCH_WATCHDOG_STATUS)
        sw_watchdog.connect("state-set", self.on_press_switch_wd)

        # Configure terminal

        terminal_label = Gtk.Label(label=self.TERMINAL_EXECUTABLE_LABEL)
        terminal_label.set_halign(Gtk.Align.START)
        terminal_entry = Gtk.Entry.new()
        terminal_entry.set_text(self.TERMINAL_COMMAND)
        terminal_entry.set_vexpand(False)
        terminal_entry.set_hexpand(True)
        terminal_entry.set_valign(Gtk.Align.CENTER)

        def on_changed_terminal(entry: Gtk.Entry):
            self.TERMINAL_COMMAND = terminal_entry.get_text()

        terminal_entry.connect("changed", on_changed_terminal)

        # add image preview and watchdog

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)

        grid.attach(img_preview_label, 0, 0, 1, 1)
        grid.attach(switch_img, 1, 0, 1, 1)
        grid.attach(watchdog_label, 0, 1, 1, 1)
        grid.attach(sw_watchdog, 1, 1, 1, 1)
        grid.attach(terminal_label, 0, 2, 1, 1)
        grid.attach(terminal_entry, 1, 2, 1, 2)

        self.append(grid)

    def on_press_switch_img(self, switch: Gtk.Switch, pspec: bool) -> None:
        """
        When change switch status, update visual on explorers
        """
        self.SWITCH_IMG_STATUS = pspec
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

    def on_press_switch_wd(self, switch: Gtk.Switch, pspec: bool) -> None:

        self.SWITCH_WATCHDOG_STATUS = pspec
        self.win.SWITCH_WATCHDOG_STATUS = pspec

        explorer_1 = self.win.explorer_1
        explorer_2 = self.win.explorer_2

        if pspec:
            explorer_1.start_watchdog(explorer_1.actual_path, explorer_1)
            explorer_2.start_watchdog(explorer_2.actual_path, explorer_2)
        else:
            explorer_1.stop_watchdog()
            explorer_2.stop_watchdog()

    def click_select_path_dialog(
        self, button: Gtk.Button, entry: Gtk.Entry
    ) -> None:
        """
        Generate FileDialog to select folder
        """

        file_dialog = Gtk.FileDialog(title=self.SELECT_FILE_TITLE)
        file_dialog.select_folder(self.win, None, self.on_file_selected, entry)

    def on_file_selected(
        self, dialog: Gtk.FileDialog, result: Gio.Task, entry: Gtk.Entry
    ) -> None:

        folder = dialog.select_folder_finish(result)
        if folder:
            if isinstance(entry, Gtk.Entry):
                value = folder.get_path()
                entry.set_text(value)
                if entry.get_name() == "path_1":
                    self.EXP_1_PATH = value

                if entry.get_name() == "path_2":
                    self.EXP_2_PATH = value

    def directory_select_option_last_dir(self, button: Gtk.Button) -> None:
        """
        Change on gui to select last dir option
        """
        self.select_directory_box_1.set_sensitive(False)
        self.select_directory_box_2.set_sensitive(False)
        self.SHOW_DIR_LAST = True

    def directory_select_option_set_dir(
        self, button: Gtk.Button, entry_1: Gtk.Entry, entry_2: Gtk.Entry
    ) -> None:
        """
        Change on gui to select set dir option
        """

        self.select_directory_box_1.set_sensitive(True)
        self.select_directory_box_2.set_sensitive(True)
        self.SHOW_DIR_LAST = False
        self.win.config.EXP_1_PATH = entry_1.get_text()
        self.win.config.EXP_2_PATH = entry_2.get_text()
