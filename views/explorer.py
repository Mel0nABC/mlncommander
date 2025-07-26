import gi, threading

# gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject, GLib
from utilities.file_manager import File_manager
from controls.Actions import Actions
from pathlib import Path
import os, asyncio
from entity.File_or_directory_info import File_or_directory_info
from utilities.my_watchdog import My_watchdog


class Explorer(Gtk.ColumnView):
    def __init__(self, name, entry):
        super().__init__()

        self.name = name
        self.actual_path = Path("/home/mel0n/Downloads/pruebas_copiar")
        self.entry = entry
        self.my_watchdog = None
        self.action = Actions()

        item_list = list(File_manager.get_path_list(self.actual_path))
        properties = [prop.name for prop in File_or_directory_info.list_properties()]
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
            column = Gtk.ColumnViewColumn.new(property_name, factory)

            # Create a Gtk.Expression for the property
            property_expression = Gtk.PropertyExpression.new(
                File_or_directory_info, None, property_name
            )

            property_type = File_or_directory_info.find_property(
                property_name
            ).value_type.fundamental

            sorter = Gtk.StringSorter.new(property_expression)

            column.set_sorter(sorter)
            column.set_expand(True)
            column.set_resizable(True)

            self.append_column(column)
            # Set the sorter on the column
            column.set_sorter(sorter)

        # DATA
        self.store = File_manager.get_path_list(self.actual_path)
        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(self.store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)

        # CONFIGURE COLUMNVIEW
        self.set_show_column_separators(True)
        self.set_vexpand(True)

        GLib.idle_add(self.update_watchdog_path, self.actual_path, self)

    def get_column_view(self):
        return self.column_view

    def get_selection(self):
        return self.selection

    def get_actual_path(self):
        return str(self.actual_path)

    def get_store(self):
        return self.store

    def load_new_path(self, path: Path):
        # Obtenemos lista de datos
        self.store = File_manager.get_path_list(path)
        self.selection = Gtk.MultiSelection.new(self.store)
        self.set_model(self.selection)
        self.actual_path = path
        self.entry.set_text(str(path))

    def remove_actual_store(self):
        self.store.remove_all()

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
