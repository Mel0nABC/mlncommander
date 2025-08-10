import threading
import asyncio
import time
import gi

from utilities.file_manager import File_manager
from controls.Actions import Actions
from pathlib import Path
from controls import Action_keys
from entity.File_or_directory_info import File_or_directory_info
from utilities.my_watchdog import My_watchdog
from icons.icon_manager import IconManager
from css.explorer_css import Css_explorer_manager

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Pango  # noqa E402


class Explorer(Gtk.ColumnView):
    def __init__(
        self,
        name: str,
        entry: Gtk.Entry,
        win: Gtk.ApplicationWindow,
        initial_path: Path,
    ):
        super().__init__()

        self.name = name
        self.focused = False
        self.actual_path = Path(initial_path)
        self.actual_path_old = None
        self.entry = entry
        self.my_watchdog = None
        self.action = Actions()
        self.css_manager = Css_explorer_manager(win)
        self.selection = None
        self.n_row = 0
        self.n_row_old = 0
        self.search_str = ""
        self.thread_reset_str = threading.Thread(target=self.str_search_start)
        self.count_rst_int = 0
        self.COUNT_RST_TIME = 5000
        self.search_str_entry = win.search_str_entry
        self.store = None
        self.win = win
        self.click_handler = 0
        self.background_list = self.get_last_child()
        self.handler_id_connect = 0
        self.flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )
        self.EXPLORER_MIRROR_KEY = "o"
        type_list = [
            "type_str",
            "name",
            "size",
            "date_created_str",
            "permissions",
        ]
        self.icon_manager = IconManager(win)

        for property_name in type_list:

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)
            column = Gtk.ColumnViewColumn.new(property_name, factory)

            # Create a Gtk.Expression for the property

            property_expression = Gtk.PropertyExpression.new(
                File_or_directory_info, None, property_name
            )

            sorter = Gtk.StringSorter.new(property_expression)

            # Column visual configuration

            column.set_sorter(sorter)
            column.set_expand(True)
            column.set_resizable(True)

            self.append_column(column)

        self.set_enable_rubberband(True)

        # Configure Gtk.ColumnView
        self.set_show_column_separators(True)
        self.set_can_focus(True)
        self.set_focusable(True)
        self.set_vexpand(True)
        self.set_hexpand(False)

        # Load css and set classes
        self.css_manager.load_css_explorer_text()
        self.css_manager.load_css_explorer_background()
        self.get_style_context().add_class("column_view_borders")
        class_name = "explorer_background"
        self.background_list.get_style_context().add_class(class_name)

        # Focus event
        self.focus_explorer = Gtk.EventControllerFocus()
        self.focus_explorer.connect(
            "enter",
            lambda controller: self.set_explorer_focus(self.win),
        )
        self.add_controller(self.focus_explorer)

        GLib.idle_add(self.update_watchdog_path, self.actual_path, self)

        # Activate pressed on explorer event
        gesture = Gtk.GestureClick()
        gesture.connect("pressed", self.set_explorer_focus)
        self.add_controller(gesture)

        # Activate shortcut Control+C
        trigger = Gtk.ShortcutTrigger.parse_string(
            f"<Control>{self.EXPLORER_MIRROR_KEY}"
        )
        action = Gtk.CallbackAction.new(self.shortcut_mirroring_folder)
        self.shortcut = Gtk.Shortcut.new(trigger, action)
        controller = Gtk.ShortcutController.new()
        controller.add_shortcut(self.shortcut)
        self.add_controller(controller)

    def shortcut_mirroring_folder(self, *args) -> None:
        """
        Actions when shortcuts is utilized
        """
        # Disconnect key controller from main window
        self.win.key_controller.disconnect(self.win.key_controller_id)

        # Returns the browser that does not contain the passed name
        other_explorer = self.win.get_other_explorer_with_name(self.name)

        if not other_explorer:
            return

        selected_item = self.get_selected_items_from_explorer()[1]

        if not selected_item:
            other_explorer.load_data(self.actual_path.parent)

        if not selected_item:
            path = self.actual_path.parent
        else:
            path = selected_item[0]

        if selected_item:
            if not path.is_dir():
                path = path.parent

        other_explorer.load_new_path(path)

        GLib.idle_add(self._reeconnect_controller)

    def _reeconnect_controller(self) -> None:
        """
        After finish utilization shortcuts, reactivate key controller
        """
        self.win.key_controller_id = self.win.key_controller.connect(
            "key-pressed",
            Action_keys.on_key_press,
            self.win,
            self.win.action,
        )

    def setup(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        """
        Configure type columnview Cell
        """

        def setup_when_idle():
            """
            Depent of type, set Gtk.Image for icons or Gtk.Label for text
            """
            if property_name == "type_str":
                image = Gtk.Image()
                cell.set_child(image)
            else:
                label = Gtk.Label(xalign=0)
                label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
                label.get_style_context().add_class("explorer_text_size")
                cell.set_child(label)

        GLib.idle_add(setup_when_idle)

    def bind(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        def bind_when_idle():
            """
            Set value for columnview cells
            """
            item = cell.get_item()
            if item:
                output_column = cell.get_child()
                value = item.get_property(property_name)
                if property_name == "type_str":
                    if item.type == "DIR":
                        pintable = self.icon_manager.get_folder_icon()
                    elif item.type == "FILE":
                        path = item.path_file
                        pintable = self.icon_manager.get_icon_for_file(path)
                    else:
                        pintable = self.icon_manager.get_back_icon()
                    output_column.set_from_paintable(pintable)
                else:
                    output_column.set_text(str(value))

        GLib.idle_add(bind_when_idle)

    def set_explorer_focus(
        self,
        obj: Gtk.GestureClick = None,
        n_press: int = None,
        x: float = None,
        y: float = None,
        win: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Bring focus to the browser when clicking
        anywhere in it. Terminates the search engine if enabled.
        """

        if self.count_rst_int > 0:
            self.count_rst_int = self.COUNT_RST_TIME
        else:
            self.action.set_explorer_to_focused(self, self.win)

    def load_data(self, path: Path) -> None:
        """
        Load information from the current directory
        """
        if self.selection:
            self.selection.unselect_all()
        self.store = File_manager.get_path_list(path)
        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(self.store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)
        self.actual_path = path
        self.entry.set_text(str(path))

    def load_new_path(self, path: Path) -> None:
        """
        Load data and display the contents
        of the current directory in the browser
        """
        # Management to save the row number when advancing a directory
        if self.actual_path_old:
            if not self.actual_path_old.is_relative_to(path):
                self.actual_path_old = self.actual_path
                self.n_row_old = self.n_row
        else:
            self.actual_path_old = self.actual_path

        self.load_data(path)

        # We reconnect if it was disconnected when entering
        # new folder
        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )

        lista_path = list(path.iterdir())
        if len(lista_path) == 0:
            GLib.idle_add(self.scroll_to, 0, None, self.flags)

        # Managing which list number to start a directory at
        # Whether to move forward or backward
        # You need to change the way you manage it, perhaps with a list,
        # Dictionary or similar
        if self.actual_path_old.is_relative_to(path):
            # Step back
            self.scroll_to(self.n_row_old, None, self.flags)
        else:
            # Keep it up
            size = len(list(self.store))
            if size == 1:
                file = 0
            else:
                file = 1
            self.scroll_to(file, None, self.flags)

        if self.count_rst_int > 0:
            self.stop_background_search()
            self.stop_search_mode()

    def on_item_change(
        self,
        obj: Gtk.MultiSelection = None,
        n_press: int = None,
        x: int = None,
        win: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Selecting another row in a browser changes
        the value of the self.n_row variable.
        Update bottom information, selected files and size
        """
        selected = self.get_selected_items_from_explorer()
        selected_items = list(selected[1])
        selected_size = len(selected_items)
        if selected_size == 1:
            self.n_row = selected[0]

        items_list_size = len(list(self.store)) - 1

        total_size_items = 0
        for item in selected_items:
            if not item.is_dir():
                if not item.is_symlink():
                    total_size_items += item.stat().st_size

        temp_file_or_directory = File_or_directory_info("/")
        total_size_items_reduced = temp_file_or_directory.get_size_and_unit(
            total_size_items
        )
        info_selected_files = (
            f"{selected_size} de {items_list_size} "
            f"seleccionados, {total_size_items_reduced}"
        )

        if self.name == "explorer_1":
            win.label_left_selected_files.set_text(info_selected_files)

        if self.name == "explorer_2":
            win.label_right_selected_files.set_text(info_selected_files)

    def get_selected_items_from_explorer(self) -> list:
        """
        Gets the selection list of an explorer
        """
        selected_items = []
        item = None
        index_return = 0
        for index in range(self.selection.get_n_items()):
            item = self.selection.get_item(index).path_file
            if self.selection.is_selected(index):
                item = self.selection.get_item(index).path_file
                if not str(item) == "..":
                    index_return = index
                    selected_items.append(item)

        return index_return, selected_items

    def update_watchdog_path(self, path: Path, explorer: "Explorer") -> None:
        """
        The watchdog route is changed
        """
        asyncio.ensure_future(self.control_watchdog(path, explorer))

    def set_str_search(self, search_word: str) -> str:
        """
        The search word is changed by
        adding characters and the timer is reset.
        """
        self.search_str = search_word

        if not self.thread_reset_str.is_alive():
            self.thread_reset_str = threading.Thread(
                target=self.str_search_start
            )
            self.thread_reset_str.start()
        self.count_rst_int = 0
        self.search_str_entry.set_text(self.search_str)
        return self.search_str

    def set_str_search_backspace(self, text: str) -> None:
        """
        The search word is changed by deleting
        characters and resetting the timer.
        """
        self.count_rst_int = 0
        self.search_str = text
        self.search_str_entry.set_text(self.search_str)

    def str_search_start(self) -> None:
        """
        Initialize proccess to search word in explorer list
        """
        self.n_row_old = self.n_row
        while self.count_rst_int < self.COUNT_RST_TIME:
            time.sleep(0.001)
            self.count_rst_int += 1
            if not self.focused:
                self.stop_search_mode()
        self.search_str = ""
        self.search_str_entry.set_text("")
        self.count_rst_int = 0
        GLib.idle_add(self.load_data, self.actual_path)
        self.stop_background_search()

    def set_background_search(self) -> None:
        """
        Search colors are activated
        """
        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

        self.handler_id_connect = self.selection.connect(
            "selection-changed", self.reset_count_rst_int
        )

        self.css_manager.load_css_background_search()
        self.background_list.get_style_context().add_class("background_search")
        self.scroll_to(0, None, self.flags)

    def stop_background_search(self):
        """
        Search colors are desactivated
        """
        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )
        self.background_list.get_style_context().remove_class(
            "background_search"
        )

    def reset_count_rst_int(
        self,
        obj: Gtk.MultiSelection = None,
        n_press: int = None,
        x: int = None,
    ) -> None:
        """
        Restablecer la temporización al escribir y seleccionar otra fila
        """
        self.count_rst_int = 0

    def stop_search_mode(self) -> None:
        """
        Finish str_search_start(self) while loop
        """
        self.count_rst_int = self.COUNT_RST_TIME

    async def control_watchdog(self, path: Path, explorer: "Explorer") -> None:
        """
        Create another watchdog with other path
        """
        if self.my_watchdog:
            self.my_watchdog.stop()
        self.my_watchdog = My_watchdog(str(path), explorer)
        self.watchdog_thread = threading.Thread(target=self.my_watchdog.start)
        self.watchdog_thread.start()
