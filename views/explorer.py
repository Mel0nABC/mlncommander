import gi, threading

# gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject, GLib
from utilities.file_manager import File_manager
from controls.Actions import Actions
from pathlib import Path
from controls import Action_keys
import os, asyncio, time
from entity.File_or_directory_info import File_or_directory_info
from utilities.my_watchdog import My_watchdog


class Explorer(Gtk.ColumnView):
    def __init__(self, name, entry, win):
        super().__init__()

        self.name = name
        self.focused = False
        self.actual_path = Path("/home/mel0n/Downloads/pruebas_copiar")
        self.entry = entry
        self.my_watchdog = None
        self.action = Actions()
        self.selection = None
        self.n_row = 0
        self.search_str = ""
        self.thread_reset_str = threading.Thread(target=self.str_search_reset)
        self.count_rst_str = 0
        self.search_str_entry = win.search_str_entry
        self.store = None
        self.win = win

        type_list = [
            "type",
            "name",
            "size",
            "date_created_str",
            "permissions",
        ]
        for property_name in type_list:

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)
            column = Gtk.ColumnViewColumn.new(str.upper(property_name), factory)

            # Create a Gtk.Expression for the property

            if property_name == "type":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "type"
                )
            elif property_name == "name":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "name"
                )
            elif property_name == "size":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "size"
                )
            elif property_name == "date_created_str":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "date_created_str"
                )
            elif property_name == "permissions":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "permissions"
                )

            sorter = Gtk.StringSorter.new(property_expression)

            column.set_sorter(sorter)
            column.set_expand(True)
            column.set_resizable(True)

            self.append_column(column)

        # LOAD DATA
        self.load_new_path(self.actual_path)

        self.set_enable_rubberband(True)

        # CONFIGURE COLUMNVIEW
        self.set_show_column_separators(True)
        self.set_vexpand(True)
        self.set_can_focus(True)
        self.set_focusable(True)

        GLib.idle_add(self.update_watchdog_path, self.actual_path, self)

        # AL HACER CLICK EN UNA FILA, SE AJUSTA self.n_row
        focus_explorer = Gtk.EventControllerFocus()
        focus_explorer.connect(
            "enter", lambda controller: self.set_explorer_focus(self.win)
        )
        self.add_controller(focus_explorer)

        print(f"INICIO EXPLORER --> {self.focused}")

    def set_explorer_focus(self, obj=None, n_press=None, x=None, y=None, win=None):
        self.on_columnview_click()
        self.action.set_explorer_src(self, self.win)

    def on_columnview_click(self):
        selected_item = list(self.action.get_selected_items_from_explorer(self))
        selected_size = len(selected_item)
        if selected_size == 1:
            self.n_row = self.get_index_in_store(self.store, selected_item[0])

    def get_index_in_store(self, store, target_item):
        for i in range(store.get_n_items()):
            if store.get_item(i).path_file == target_item:
                return i
        return -1  # No encontrado

    def get_column_view(self):
        return self.column_view

    def get_selection(self):
        return self.selection

    def get_actual_path(self):
        return str(self.actual_path)

    def get_store(self):
        return self.store

    def load_new_path(self, path: Path):
        if self.store:
            self.remove_actual_store()
        self.store = File_manager.get_path_list(path)
        self.apply_model_changes(self.store)
        self.actual_path = path
        self.entry.set_text(str(path))
        # AL HACER CLICK EN UNA FILA, SE AJUSTA self.n_row
        self.selection.connect("selection-changed", self.set_explorer_focus, self.win)

    def remove_actual_store(self):
        self.set_model(None)
        self.store.remove_all()

    def set_new_store(self, item_list):
        self.remove_actual_store()
        self.store = Gio.ListStore.new(File_or_directory_info)
        for item in item_list:
            print(item)
            self.store.append(item)
        self.apply_model_changes(self.store)

    def apply_model_changes(self, store):
        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)
        self.n_row = 1

    def update_watchdog_path(self, path, explorer):
        asyncio.ensure_future(self.control_watchdog(path, explorer))

    async def control_watchdog(self, path, explorer):
        if self.my_watchdog:
            self.my_watchdog.stop()
            # self.watchdog_thread.join()
        self.my_watchdog = My_watchdog(str(path), explorer)
        self.watchdog_thread = threading.Thread(target=self.my_watchdog.start)
        self.watchdog_thread.start()

    def get_watchdog(self):
        return self.my_watchdog

    def setup(self, signal, cell, property_name):
        label = Gtk.Label(xalign=0)
        cell.set_child(label)

    def bind(self, signal, cell, property_name):
        item = cell.get_item()
        label = cell.get_child()
        value = item.get_property(property_name)
        label.set_text(str(value))

    def set_str_search(self, char):
        self.search_str += char

        if not self.thread_reset_str.is_alive():
            self.thread_reset_str = threading.Thread(target=self.str_search_reset)
            self.thread_reset_str.start()
        self.count_rst_str = 0
        self.search_str_entry.set_text(self.search_str)
        return self.search_str

    def set_str_search_backspace(self, text):
        self.count_rst_str = 0
        self.search_str = text
        self.search_str_entry.set_text(self.search_str)

    def str_search_reset(self):
        while self.count_rst_str < 1:
            time.sleep(1)
            self.count_rst_str += 1

        self.search_str = ""
        self.search_str_entry.set_text("")
        flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )

        self.scroll_to(1, None, flags)
        GLib.idle_add(self.load_new_path, self.actual_path)
        self.grab_focus()
