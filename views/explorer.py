import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject
from utilities.file_manager import File_manager
from pathlib import Path
import os
from entity.File_or_directory_info import File_or_directory_info


class Explorer(Gtk.Widget):
    def __init__(self, name):
        self.name = name
        self.actual_path = Path("/media/Almacenamiento/Download/pruebas_copiar")

        # Obtenemos lista de datos
        self.store = File_manager.get_path_list(self.actual_path)

        # Envoltorio que se conecta al modelo y permite seleccionar varios objetos
        self.selection = Gtk.MultiSelection.new(self.store)

        # el widget que mostrará la información

        self.column_view = Gtk.ColumnView.new(self.selection)
        self.column_view.set_show_column_separators(True)

        # self.column_view.set_show_row_separators(True)
        # self.column_view.set_single_click_activate(True) # Para activar elementos con un solo click
        # Gtk.ColumnView.set_single_click_activate(self.column_view, True)

        # Creamos columnas
        factory_type = Gtk.SignalListItemFactory.new()
        factory_type.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory_type.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                item.get_item().get_property("type")
            ),
        )

        factory_name = Gtk.SignalListItemFactory.new()
        factory_name.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory_name.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                item.get_item().get_property("name")
            ),
        )

        factory_size = Gtk.SignalListItemFactory.new()
        factory_size.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory_size.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                item.get_item().get_property("size")
            ),
        )

        factory_date = Gtk.SignalListItemFactory.new()
        factory_date.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory_date.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                item.get_item().get_property("date_created_str")
            ),
        )

        factory_permission = Gtk.SignalListItemFactory.new()
        factory_permission.connect(
            "setup", lambda factory, item: item.set_child(Gtk.Label(xalign=0))
        )
        factory_permission.connect(
            "bind",
            lambda factory, item: item.get_child().set_text(
                item.get_item().get_property("permissions")
            ),
        )

        column_type = Gtk.ColumnViewColumn(title="Tipo", factory=factory_type)
        column_name = Gtk.ColumnViewColumn(title="Nombre", factory=factory_name)
        column_size = Gtk.ColumnViewColumn(title="Tamaño", factory=factory_size)
        column_date = Gtk.ColumnViewColumn(title="Fecha", factory=factory_date)
        column_permission = Gtk.ColumnViewColumn(
            title="Permisos", factory=factory_permission
        )

        column_type.set_expand(True)
        column_name.set_expand(True)
        column_size.set_expand(True)
        column_date.set_expand(True)
        column_permission.set_expand(True)

        column_type.set_resizable(True)
        column_name.set_resizable(True)
        column_size.set_resizable(True)
        column_date.set_resizable(True)
        column_permission.set_resizable(True)

        # column_type.set_min_width(100)
        # column_name.set_resizable(True)
        # column_size.set_resizable(True)
        # column_date.set_resizable(True)
        # column_permission.set_resizable(True)

        self.column_view.append_column(column_type)
        self.column_view.append_column(column_name)
        self.column_view.append_column(column_size)
        self.column_view.append_column(column_date)
        self.column_view.append_column(column_permission)

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
        # Envoltorio que se conecta al modelo y permite seleccionar varios objetos
        self.selection = Gtk.MultiSelection.new(self.store)
        self.column_view.set_model(self.selection)
        self.actual_path = path

    def remove_actual_store(self):
        self.store.remove_all()
